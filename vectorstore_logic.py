# region Imports
import os, shutil, tempfile, requests, hashlib
import json, re
from pathlib import Path
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Vector store creation and management for One Piece Card Game rules
# This implementation handles loading the rules from PDF files, checking for updates, and managing the vector store.
# Namely, it operates in a `.cache/optcg_rulebooks_vectorstore` directory in the user's home directory.
# The vector store is created using the Chroma library with OpenAI embeddings.

# TODO: See region "Hashing and Updating"

# Main Functions: 
# - loader_optcg_rulebooks
# - create_or_load_vectorstore_optcg_rulebooks
# - check_for_updates_to_rules
# - delete_vectorstore_optcg_rulebooks


# All Functions:
# - load_pdf_from_url: Load a PDF from a URL and extract its text content
# - loader_optcg_rulebooks: Load the One Piece Card Game rules from the official website

# - hash_documents: Create a unique hash for the documents
# - save_hash: Save the hash of the documents to a file
# - load_hash: Load the hash of the documents from a file

# - check_document_changes: Check if the documents have changed since the last time the vector store was created
# - check_for_updates_to_rules: Check if the One Piece Card Game rules have been updated since the last vector store creation, using the hash of the documents

# - preprocess_tournament_rules: Add custom separators for tournament rule numbering to improve document chunking and retrieval
# - create_or_load_vectorstore_optcg_rulebooks: Create or load the persistent vector store for the One Piece Card Game rules
# - delete_vectorstore_optcg_rulebooks: Delete the persistent vector store for One Piece Card Game rules


# endregion Imports



# region Document Loading

## Dummy PDF URL for testing purposes to reduce embedding costs with OpenAI
# docs = load_pdf_from_url("https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")

def load_pdf_from_url(url: str):
    """
    Load a PDF from a URL and extract its text content.
    
    Args:
        url: The URL of the PDF file
    
    Returns:
        List of documents with page content
    """
    try:
        # Download the PDF content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        # Load the PDF using PyPDFLoader
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return documents
    
    except Exception as e:
        print(f"Error loading PDF from URL: {str(e)}")
        return None
    
def loader_optcg_rulebooks():
    """
    Load the One Piece Card Game rules from the official website.
    
    Returns:
        List of documents with page content
    """
    comp_rules = load_pdf_from_url("https://en.onepiece-cardgame.com/pdf/rule_comprehensive.pdf?20250221")
    tourney_rules = load_pdf_from_url("https://en.onepiece-cardgame.com/pdf/tournament_rules_manual.pdf?20250613")
    
    # Verifies BOTH comprehensive and tournament rules are loaded
    # If either is None, it means loading failed
    # Ensures we have both sets of rules before proceeding
    if comp_rules is None or tourney_rules is None:
        print("Failed to load One Piece Card Game rules.")
        print("Please check the URLs or your internet connection.")
        return None, None# Exit early if loading fails
    
    # Tag each page/chunk with its source
    for page in comp_rules:
        page.metadata["source"] = "comprehensive_rules"
    for page in tourney_rules:
        page.metadata["source"] = "tournament_rules"

    return comp_rules, tourney_rules

# endregion Document Loading



# region Hashing and Updating

## NOTE: Hashing function to create a unique hash for the documents
# This is used to check if the documents have changed since the last time the vector store was created
# i.e. if the documents have been updated.

## TODO: The `check_for_updates_to_rules` function only implements the check for updates to the rules. This function does not update the vector store.
# Would need to call `create_or_load_vectorstore_optcg_rulebooks()` to create the vector store if updates are detected.
# If there is an existing vector store, it should be deleted and a new one will be created.

def hash_documents(documents):
    combined = "".join(doc.page_content for doc in documents)
    return hashlib.md5(combined.encode("utf-8")).hexdigest()

def save_hash(doc_hash, HASH_PATH):
    with open(HASH_PATH, "w") as f:
        json.dump({"hash": doc_hash}, f)

def load_hash(HASH_PATH):
    if HASH_PATH.exists():
        with open(HASH_PATH, "r") as f:
            return json.load(f).get("hash")
    return None

def check_document_changes(documents, HASH_PATH, PERSIST_DIR_IN_CACHE="optcg_rulebooks_vectorstore"): 
    """
    Check if the documents have changed since the last time the vector store was created.
    This should never return `False, False` as at document hash should always be created when the vector store is created.
    """
    current_hash = hash_documents(documents)
    saved_hash = load_hash(HASH_PATH)
    
    CACHE_DIRECTORY = Path.home() / ".cache"
    CACHE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    PERSIST_DIRECTORY = CACHE_DIRECTORY / PERSIST_DIR_IN_CACHE

    if saved_hash is None:
        if os.path.exists(PERSIST_DIRECTORY) and os.listdir(PERSIST_DIRECTORY):
            print("WARNING: Previous hash not found, but vector store exists. This is unexpected!")
            print("Please delete the existing vector store and create a new one to ensure hash is created.")
            return False, False # This should not happen! Hash should always be created when the vector store is created.
        print("No previous hash found. Create a new vector store.")
        return False, True  # No previous hash, so we need to create a new vector store
    elif current_hash != saved_hash:
        print("Documents have changed since last vector store creation.")
        return True, True  # Documents have changed, so we need to create a new vector store
    elif current_hash == saved_hash:
        print("Documents have not changed since last vector store creation.")
        return True, False  # No changes detected

def check_for_updates_to_rules():
    """Check if the One Piece Card Game rules have been updated since the last vector store creation, using the hash of the documents"""
    CACHE_DIRECTORY = Path.home() / ".cache"
    CACHE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    PERSIST_DIR_IN_CACHE="optcg_rulebooks_vectorstore"
    PERSIST_DIRECTORY = CACHE_DIRECTORY / PERSIST_DIR_IN_CACHE
    HASH_PATH = PERSIST_DIRECTORY / "doc_hash.json"

    comp_rules, tourney_rules = loader_optcg_rulebooks()
    if comp_rules is not None and tourney_rules is not None: # Exit if no documents are loaded.
        documents = comp_rules + tourney_rules
        existing_hash_bool, doc_changes_bool = check_document_changes(documents, HASH_PATH, PERSIST_DIR_IN_CACHE) # type: ignore
        print(f"Existing hash found: {existing_hash_bool}, Document changes detected: {doc_changes_bool}")
        if not doc_changes_bool:
            print("No updates needed.")
            return False
        elif not existing_hash_bool and doc_changes_bool:
            print("Documents have changed or no previous hash found. Create a new vector store.")
            return True       
        elif existing_hash_bool and doc_changes_bool:
            print("Update needed. Delete existing vector store and create a new one.")
            return True
        else: # If check_document_changes returns as `False, False`, this is unexpected.
            # This should not happen! Hash should always be created when the vector store is created.
            print("Unexpected case. Please check the implementation.")
            return None
    else:
        print("Cannot check for updates. No documents loaded.")
        return None
# endregion Hashing and Updating



# region Vector Store Creation and Management

def preprocess_tournament_rules(documents):
    """
    Add custom separators for tournament rule numbering
    Used to improve document chunking and retrieval.
    """
    processed_docs = []
    
    for doc in documents:
        # Replace patterns like "1.2 followed by 1.2.1" with double newlines
        content = doc.page_content
        
        # Add double newlines (`\n\n`) before numbered sections like "1.2" and "1.2.1"
        content = re.sub(r'(\d+\.\d+)', r' \n\n\1', content)
        #content = re.sub(r'(\d+\.\d+\.\d+)', r' \n\n\1', content)

        # Create new document with processed content
        new_doc = doc.model_copy()
        new_doc.page_content = content
        processed_docs.append(new_doc)
    
    return processed_docs

def create_or_load_vectorstore_optcg_rulebooks():
    """Create or load the persistent vector store for the One Piece Card Game rules. Using Chroma and OpenAI embeddings."""
    
    # Define the cache directory and persistent directory
    CACHE_DIRECTORY = Path.home() / ".cache"
    CACHE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    PERSIST_DIRECTORY = CACHE_DIRECTORY / "optcg_rulebooks_vectorstore"

    # Define the embedding model
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large"
        )

    # Check if vector store already exists and load it
    if os.path.exists(PERSIST_DIRECTORY) and os.listdir(PERSIST_DIRECTORY):
        print("Loading existing vector store...")
        vectorstore = Chroma(
            persist_directory=str(PERSIST_DIRECTORY),
            embedding_function=embeddings
        )
        return vectorstore
    
    # If vector store does not exist, create it
    else: 
        print("Creating new vector store...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=300,
            separators=["\n\n", "\n \n", "\n", ". ", " ", ""]
        )
        
        # Load and split documents
        comp_rules, tourney_rules = loader_optcg_rulebooks()
        if not comp_rules or not tourney_rules:
            print("No documents loaded. Please check PDF URLs.")
            return None # Exit if no documents are loaded. Will not create a vector store.
        docs = comp_rules + tourney_rules
        doc_chunks = text_splitter.split_documents(docs)
        print(f"Split documents into {len(doc_chunks)} chunks")
        
        # Create vector store with persistence
        vectorstore = Chroma.from_documents(
            documents=doc_chunks,
            embedding=embeddings,
            persist_directory=str(PERSIST_DIRECTORY)
        )
        print(f"Vector store created and saved to {PERSIST_DIRECTORY}")


        HASH_PATH = PERSIST_DIRECTORY / "doc_hash.json"
        docs_hash = hash_documents(docs)
        save_hash(docs_hash, HASH_PATH)
        print(f"Document hash saved to {HASH_PATH}")

        return vectorstore
    

### NOTE: The following function is for deleting the vector store from disk.
## This should only be used if you need to update the vector store with new documents or changes. Otherwise, only if you absoutely need to delete the vector store from the disk. 

## The implentation of storing the vector store on disk is to ensure that it persists across sessions and does not need to be recreated every time you run the code. Limiting the need to re-embed the documents every time you run the code. Thus, reducing costs and improving performance.

def delete_vectorstore_optcg_rulebooks():
    """Delete the persistent vector store for One Piece Card Game rules"""
    
    # Rudimentary confirmation prompt
    confirmation = input("Are you sure you want to delete the vector store? This action cannot be undone. Type 'yes' to confirm: ")
    if confirmation.strip().lower() != 'yes':
        print("Deletion cancelled.")
        return
    
    # Delete the vector store directory if it exists
    PERSIST_DIRECTORY = Path.home() / ".cache" / "optcg_rulebooks_vectorstore"
    if PERSIST_DIRECTORY.exists():
        try:
            # Use shutil.rmtree to recursively delete the entire directory tree
            shutil.rmtree(PERSIST_DIRECTORY)
            print(f"Deleted vector store at {PERSIST_DIRECTORY}")
        except PermissionError as e:
            print(f"Permission error: {e}")
            print("Please ensure no files are open in the vector store directory.")
            print("You may need to close any applications using the vector store before deleting it. Try restarting your Jupyter kernel and running delete again.")
        except Exception as e:
            print(f"Error deleting vector store: {e}")
    else:
        print("No vector store found to delete.")

# endregion Vector Store Creation and Management