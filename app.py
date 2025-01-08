import streamlit as st
import validators


from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptAvailable, VideoUnavailable
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.schema import Document


# Streamlit App Configuration
st.set_page_config(
    page_title="LangChain: Summarize Text From YT or Website",
    page_icon="📚"
)
st.title("📚 LangChain: Summarize Text From YT or Website")
st.subheader("Summarize URL")

# Sidebar for Groq API Token
with st.sidebar:
    groq_api_key = st.text_input("Groq API Token", value="", type="password")

# Input URL (YouTube or Website)
generic_url = st.text_input("URL", label_visibility="collapsed")

# Groq Model Setup
llm = ChatGroq(model="gemma2-9b-it", groq_api_key=groq_api_key)

# Prompt Template for Summarization
prompt_template = """
Provide a summary of the following content in 300 words:
Content: {text}
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

def get_youtube_transcript(video_url):
    """
    Function to extract transcript from a YouTube video.
    """
    try:
        video_id = video_url.split("v=")[-1].split("&")[0]


        transcript = YouTubeTranscriptApi.get_transcript(video_id)


        text = " ".join([item["text"] for item in transcript])
        return text



    except NoTranscriptAvailable:
        raise Exception("No transcript available for this video.")

   

    except VideoUnavailable:
        raise Exception("The video is unavailable.")
    
# Handle Video Unavailability:
# Catches exceptions if the video is private, deleted, or restricted in certain regions.
    except Exception as e:
        raise Exception(f"An error occurred while fetching transcript: {e}")
# Generic Error Handling:
# Handles any other unexpected errors and includes the error details in the message.

if st.button("Summarize the Content from YT or Website"):

#  Button: Adds a button to the Streamlit app. When clicked, the following block of code executes.
   
    # Validate Inputs
    if not groq_api_key.strip() or not generic_url.strip():
        st.error("Please provide the required information to get started.")



    elif not validators.url(generic_url):
        st.error("Invalid URL format. Please enter a valid YouTube or website URL.")
    else:
        try:
            with st.spinner("Extracting and summarizing content..."):
                # Load content from YouTube or Website
                if "youtube.com" in generic_url:
                    transcript_text = get_youtube_transcript(generic_url)
                    docs = [Document(page_content=transcript_text)]
                else:
                    loader = UnstructuredURLLoader(
                        urls=[generic_url],
                        ssl_verify=False,
                        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
                    )
                    docs = loader.load()
                # Summarization Chain
                chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                output_summary = chain.run(docs)

                # Display Summary
                st.success("Summary:")
                st.write(output_summary)

# Displays a success message along with the generated summary.

        except Exception as e:
            st.error(f"An error occurred: {e}")
