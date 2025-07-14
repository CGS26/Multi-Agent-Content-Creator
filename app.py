import streamlit as st
import os
import tempfile
from agents.MultiAgentOrchestrator import MultiAgentOrchestrator

st.set_page_config(page_title="PDF to SQL Generator", layout="centered")
st.title("📄 PDF to SQL Generator")

st.markdown("""
This app lets you convert PDFs into SQL queries using AI. 
Choose between processing a single PDF or multiple PDFs from a folder.
""")

# Create tabs for different processing modes
tab1, tab2 = st.tabs(["Single PDF", "Folder Processing"])

with tab1:
    st.header("Process Single PDF")
    
    # --- File upload ---
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"], key="single_pdf")
    
    # --- Output directory ---
    default_output_dir = os.path.join(os.getcwd(), "output")
    output_dir = st.text_input("Output Directory", value=default_output_dir, key="single_output_dir")
    
    # --- Number of sections ---
    num_sections = st.number_input("Number of Sections (leave blank for default)", min_value=1, step=1, format="%d", value=None, placeholder="e.g. 5", key="single_sections")
    
    # --- Subject ---
    subject = st.text_input("Subject", value="Mathematics", key="single_subject")
    
    # --- Max Chunks ---
    max_chunks_input = st.text_input("Max Chunks (leave blank for all)", value="", placeholder="e.g. 10", key="single_chunks")
    max_chunks = int(max_chunks_input) if max_chunks_input.strip().isdigit() else None
    
    # --- Supabase Configuration (Optional) ---
    st.markdown("### 🗄️ Supabase Configuration (Optional)")
    enable_supabase = st.checkbox("Enable Supabase Insertion", key="single_enable_supabase")
    
    if enable_supabase:
        supabase_url = st.text_input("Supabase URL", placeholder="https://your-project.supabase.co", key="single_supabase_url")
        supabase_key = st.text_input("Supabase API Key", type="password", placeholder="your-api-key", key="single_supabase_key")
        table_name = st.text_input("Table Name", placeholder="lessons", key="single_table_name")
    
    # --- Run button ---
    run_single_btn = st.button("Run Single PDF Pipeline", key="run_single")
    
    if run_single_btn:
        if not pdf_file:
            st.error("Please upload a PDF file.")
        else:
            with st.spinner("Processing PDF and generating SQL..."):
                # Save uploaded PDF to a temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                    tmp_pdf.write(pdf_file.read())
                    tmp_pdf_path = tmp_pdf.name

                # Ensure output directory exists
                os.makedirs(output_dir, exist_ok=True)

                # Prepare orchestrator arguments
                orchestrator = MultiAgentOrchestrator()
                kwargs = {
                    "pdf_path": tmp_pdf_path,
                    "subject": subject,
                    "course_id": None,
                    "max_chunks": max_chunks,
                    "num_sections": num_sections
                }
                try:
                    results = orchestrator.process_pdf_to_sql(**kwargs)
                    st.success("Pipeline completed!")
                    
                    # Always show file downloads
                    st.markdown("### 📁 Output Files:")
                    for key in ["structured_sections_file", "lessons_file", "sql_file"]:
                        file_path = results.get(key)
                        if file_path and os.path.exists(file_path):
                            st.write(f"{key.replace('_', ' ').title()}: {file_path}")
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label=f"Download {os.path.basename(file_path)}",
                                    data=f,
                                    file_name=os.path.basename(file_path),
                                    key=f"single_download_{key}"
                                )
                    
                    # Optional Supabase insertion
                    if enable_supabase and supabase_url and supabase_key and table_name:
                        st.markdown("### 🗄️ Supabase Insertion:")
                        with st.spinner("Inserting data to Supabase..."):
                            try:
                                # Import and use Supabase client
                                from supabase import create_client, Client
                                
                                supabase_single: Client = create_client(supabase_url, supabase_key)
                                
                                # Load lessons data and insert
                                lessons_file = results.get('lessons_file')
                                if lessons_file and os.path.exists(lessons_file):
                                    import json
                                    with open(lessons_file, 'r', encoding='utf-8') as f:
                                        lessons_data = json.load(f)
                                    
                                    # Insert data to Supabase
                                    response = supabase_single.table(table_name).insert(lessons_data).execute()
                                    
                                    if response.data:
                                        st.success(f"✅ Successfully inserted {len(response.data)} records to Supabase table '{table_name}'")
                                    else:
                                        st.warning("⚠️ No data was inserted to Supabase")
                                        
                            except Exception as e:
                                st.error(f"❌ Supabase insertion failed: {e}")
                    elif enable_supabase:
                        st.warning("⚠️ Supabase insertion skipped - missing URL, API key, or table name")
                    
                    st.markdown(f"**Subject:** {results.get('subject')}")
                    st.markdown(f"**Total sections processed:** {results.get('total_sections')}")
                    st.markdown(f"**Total lessons:** {results.get('total_lessons')}")
                    st.markdown(f"**Total SQL queries:** {results.get('total_sql_queries')}")
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_pdf_path):
                        os.remove(tmp_pdf_path)

with tab2:
    st.header("Process Folder of PDFs")
    
    # --- Folder path ---
    folder_path = st.text_input("Folder Path (containing PDFs)", placeholder="e.g. /path/to/pdf/folder", key="folder_path")
    
    # --- Course ID ---
    course_id = st.text_input("Course ID", placeholder="e.g. MATH101", key="course_id")
    
    # --- Output directory ---
    default_folder_output_dir = os.path.join(os.getcwd(), "output")
    folder_output_dir = st.text_input("Output Directory", value=default_folder_output_dir, key="folder_output_dir")
    
    # --- Max Documents ---
    max_docs_input = st.text_input("Max Documents (leave blank for all)", value="", placeholder="e.g. 5", key="max_docs")
    max_docs = int(max_docs_input) if max_docs_input.strip().isdigit() else None
    
    # --- Max Chunks per Document ---
    max_chunks_per_doc_input = st.text_input("Max Chunks per Document (leave blank for all)", value="", placeholder="e.g. 10", key="max_chunks_per_doc")
    max_chunks_per_doc = int(max_chunks_per_doc_input) if max_chunks_per_doc_input.strip().isdigit() else None
    
    # --- Subject ---
    folder_subject = st.text_input("Subject", value="Mathematics", key="folder_subject")
    
    # --- Supabase Configuration (Optional) ---
    st.markdown("### 🗄️ Supabase Configuration (Optional)")
    enable_supabase = st.checkbox("Enable Supabase Insertion", key="folder_enable_supabase")
    
    if enable_supabase:
        supabase_url = st.text_input("Supabase URL", placeholder="https://your-project.supabase.co", key="folder_supabase_url")
        supabase_key = st.text_input("Supabase API Key", type="password", placeholder="your-api-key", key="folder_supabase_key")
        table_name = st.text_input("Table Name", placeholder="lessons", key="folder_table_name")
    
    # --- Run button ---
    run_folder_btn = st.button("Run Folder Processing Pipeline", key="run_folder")
    
    if run_folder_btn:
        if not folder_path:
            st.error("Please enter a folder path.")
        elif not course_id:
            st.error("Please enter a Course ID.")
        elif not os.path.exists(folder_path):
            st.error("Folder path does not exist.")
        else:
            with st.spinner("Processing PDFs in folder..."):
                # Ensure output directory exists
                os.makedirs(folder_output_dir, exist_ok=True)
                
                orchestrator = MultiAgentOrchestrator()
                try:
                    results = orchestrator.process_folder_to_sql(
                        folder_path=folder_path,
                        course_id=course_id,
                        max_docs=max_docs,
                        subject=folder_subject,
                        max_chunks_per_doc=max_chunks_per_doc,
                        output_dir=folder_output_dir
                    )
                    
                    st.success("Folder processing completed!")
                    
                    # Always show file downloads
                    st.markdown("### 📁 Output Files:")
                    combined_sql_file = results.get('combined_sql_file')
                    if combined_sql_file and os.path.exists(combined_sql_file):
                        st.write(f"Combined SQL File: {combined_sql_file}")
                        with open(combined_sql_file, "rb") as f:
                            st.download_button(
                                label="Download Combined SQL File",
                                data=f,
                                file_name=os.path.basename(combined_sql_file),
                                key="folder_download_sql"
                            )
                    
                    # Optional Supabase insertion
                    if enable_supabase and supabase_url and supabase_key and table_name:
                        st.markdown("### 🗄️ Supabase Insertion:")
                        with st.spinner("Inserting data to Supabase..."):
                            try:
                                # Import and use Supabase client
                                from supabase import create_client, Client
                                
                                supabase_folder: Client = create_client(supabase_url, supabase_key)
                                
                                # For folder processing, we need to collect all lessons from individual PDFs
                                # This would require modifying the orchestrator to return lessons data
                                st.info("ℹ️ Supabase insertion for folder processing requires additional implementation")
                                
                            except Exception as e:
                                st.error(f"❌ Supabase insertion failed: {e}")
                    elif enable_supabase:
                        st.warning("⚠️ Supabase insertion skipped - missing URL, API key, or table name")
                    
                    # Display results
                    st.markdown("### 📊 Processing Summary:")
                    st.markdown(f"**Course ID:** {results.get('course_id')}")
                    st.markdown(f"**Subject:** {results.get('subject')}")
                    st.markdown(f"**PDFs Processed:** {results.get('total_pdfs_processed')}")
                    st.markdown(f"**PDFs Failed:** {results.get('total_pdfs_failed')}")
                    
                    # Show processed files
                    if results.get('processed_files'):
                        st.markdown("**Successfully Processed Files:**")
                        for file in results.get('processed_files', []):
                            st.write(f"✅ {file}")
                    
                    # Show failed files
                    if results.get('failed_files'):
                        st.markdown("**Failed Files:**")
                        for file in results.get('failed_files', []):
                            st.write(f"❌ {file}")
                    
                except Exception as e:
                    st.error(f"Error: {e}") 