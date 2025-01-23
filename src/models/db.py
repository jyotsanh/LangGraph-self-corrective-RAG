# libs
from libs.libs import *

#state
from core.state import *

# importing langchain community
from langchain_community.document_loaders import PyMuPDFLoader


class VectorStore:
    def __init__(self, **kwargs:StoreArguments):
        self.store_type  = kwargs.get('store_type', None)
        self.host=host # -> milvus server host name
        self.port=port # -> milvus server port
        self.path: str =kwargs.get('path') # -> file path for csv, pdf, json, markdown
        self.collection_name: str =  kwargs.get('collection_name',None)
        self.embeddings = kwargs.get('embeddings')
        self.docs = []
        self.csv_docs = []
        self.pdf_docs = []
        self.json_docs = []
        self.md_docs = []
    
    

    def create_document(self, max_chunk_size:int= 100):
        # To get the file path (csv, pdf, json only works for now)
        """
        Reads the file from the given path and creates a list of Document objects, given a file type (csv, pdf, json, md)
        
        :param 
        - max_chunk_size: the maximum size of each chunk of text to be created as a document
        
        :return
        - a list of Document objects
        """
        file_type = self.path.split(".")[-1] #-> To get the file type for eg. csv, pdf, json, md
        print(f" \n file type is {file_type} \n")
        
        if file_type == "csv": # -> returning the csv docs
            loader = CSVLoader(self.path)
            csv_data = loader.load_and_split()
            for i in range(len(csv_data)):
                self.csv_docs.append(Document(page_content=csv_data[i].page_content))
            return self.csv_docs
        
        elif file_type == "pdf": # -> returning the pdf docs
            loader = PyMuPDFLoader(self.path)
            pdf_data = loader.load_and_split()
            for i in range(len(pdf_data)):
                self.pdf_docs.append(Document(page_content=pdf_data[i].page_content))
            
            return self.pdf_docs
            
        elif file_type == "json": # -> returning the json docs
            try:
                with open(self.path, "r") as f:
                    docs_json = json.load(f)
                splitter = RecursiveJsonSplitter(max_chunk_size=max_chunk_size)
                splited_json = splitter.split_json(docs_json)
                json_documents = splitter.create_documents(splited_json,)
                for i in range(len(json_documents)):
                    self.json_docs.append(Document(page_content=json_documents[i].page_content))
                    self.json_docs = self.json_docs + [Document(page_content=json_documents[i].page_content)]
                    
                return self.json_docs
            except Exception as e:
                return e
        
        elif file_type == "md": # -> returning the md docs
            try:
                print("the path is",self.path)
                # Since the text file contains markdown content
                loader = UnstructuredMarkdownLoader(self.path)
                
                
                #######---------------------------------Old Technique-------------------------------------###
                # markdown_data = loader.load_and_split()
                # for document in markdown_data:
                #     self.md_docs.append(
                #             Document(
                #                 page_content=document.page_content,
                #                 metadata=document.metadata
                #             )   
                #         )
                #######---------------------------------Old Technique-------------------------------------###
                
                ####------------------New Technique-------------------------------------------------####
                document = loader.load()
                # Then create a text splitter
                text_splitter = MarkdownTextSplitter(
                    chunk_size = 1000,  # Number of characters per chunk
                    chunk_overlap = 300,  # Number of characters to overlap between chunks
                    length_function = len,
                
                )
                # Split the document into chunks
                chunks = text_splitter.split_documents(document)
                # Process and store the chunks with enhanced metadata
                self.md_docs.extend([
                    Document(
                        page_content=chunk.page_content,
                        metadata={
                            **chunk.metadata,
                            'chunk_index': i,
                            'total_chunks': len(chunks),
                            'file_path': self.path,
                            'file_type': 'markdown'
                        }
                    )
                    for i, chunk in enumerate(chunks)
                ])
                    
                ########---------------------------------New Technique-------------------------------------###
                
                
                print(f"return the md docs, {len(self.md_docs)}")
                return self.md_docs
            except Exception as e:
                print(e)
            
        else:
            return f"file type error. Allowed file types are .csv, .pdf, .json, .txt only "  

    def create_vector_store(self,max_chunk_size:int= 100):
        """
        Creates a vector store (Milvus or Chroma) given the file path and collection name.
        
        :param max_chunk_size: The maximum size of each chunk of text to be created as a document
        
        :return
        - A dictionary indicating the status of the vector store creation, the type of vector store created and the name of the collection.
        """
        
        if self.store_type ==VectorDB.MILVUS:
            print("the collection name is",self.collection_name)
            splits = self.create_document(max_chunk_size=max_chunk_size) # -> function that return Document object list which is then passed to Milvus
            # print("==================================================")
            # print(splits)
            # print("==================================================")
            print("the uri is",URI)
            print("the host is",host)
            print("the port is",port)
            vectorstore_milvus= Milvus.from_documents(
                                                embedding=self.embeddings,  # -> embeddings
                                                documents=splits, 
                                                connection_args = {"uri": URI}, #-> URI represents the milvus server url with it's port
                                                collection_name=self.collection_name #-> collection name of the vectore store
                                                )
            if vectorstore_milvus:
                response={
                    "status": "success",
                    "type": "Milvus",
                    "collection_name":self.collection_name
                          }
                return response
            else:
                return "error"
            # return vectorstore_milvus

        elif self.store_type == VectorDB.CHROMA:
                splits = self.create_document()  
                vectorstore_chroma = Chroma.from_documents(
                                                documents = splits, 
                                                embedding=self.embeddings, 
                                                persist_directory=f"./Chroma/{self.collection_name}_Chroma"
                                                )

                message = f"Chroma of the name {self.collection_name} has been updated."
                response = {
                        "status": message, 
                        "collection name": self.collection_name
                        } # -> is removed from .env
                if vectorstore_chroma:
                    return response


    def get_vector_store(self):
        """
        Retrieve a vector store instance given the type of vector store and the collection name
        
        Parameters:
        - self (VectorStore): The VectorStore instance
        - store_type (VectorDB): The type of vector store, either VectorDB.MILVUS or VectorDB.CHROMA
        - collection_name (str): The name of the collection to retrieve
        
        Returns:
        - The vector store instance if it exists, otherwise None
        """
        try:
            print(f"the store_type name is {self.store_type}, {VectorDB.MILVUS}")
            if self.store_type == "milvus":
                print("brodaaaaa")
                vectorstore=Milvus(
                                    embedding_function=self.embeddings,
                                   connection_args = {"uri": URI},
                                   collection_name=self.collection_name
                                   )
                print("returning the Milvus vector store")
                return vectorstore

            elif self.store_type == VectorDB.CHROMA:
                collection_name = self.collection_name
                vectorstore = Chroma(
                                embedding_function=self.embeddings,
                                persist_directory=f"./Chroma/{collection_name}_Chroma"
                                )
                return vectorstore
            else:
                print("The vector store you are looking for does not exist. Please create a new one or correct the collection name of the vector store")
        except Exception as e :
            print(e)
            return e
        
