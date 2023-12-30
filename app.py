import streamlit as st
import time
import openai
import pandas as pd
#from feedgen.feed import FeedGenerator
import datetime
import base64 
import re #Use regular expression
from dotenv import load_dotenv
import os
from st_paywall import add_auth

load_dotenv()  # Load environment variables from .env file
openai_api_key = os.getenv('OPENAI_API_KEY')

add_auth(required = True)

"""
#Creation of rssFeed
def rssFeed(passed_content):
    # Create a feed generator object
    fg = FeedGenerator()
    fg.title('macaws.ai Social Media Feed')
    fg.link(href='http://macaws.ai', rel='alternate')
    fg.description('This is a test RSS feed')

    # Add items to the feed
    for i, content in enumerate(passed_content):
        #The title of the RSS feed is the date which they created.
        current_datetime = datetime.datetime.now()
        fe = fg.add_entry()
        fe.title(f'Item {i} - {current_datetime.strftime("%Y-%m-%d %H:%M:%S")}')
        fe.link(href=f'http://macaws.ai/r2r')
        fe.description(content)

    # Generate the RSS feed
    rssfeed = fg.rss_str(pretty=True)



    # Write to a file with UTF-8 encoding
    with open('rssfeed.xml', 'w', encoding='utf-8') as f:
        # Check if rssfeed is a bytes object and decode if necessary
        if isinstance(rssfeed, bytes):
            rssfeed = rssfeed.decode('utf-8')
        f.write(rssfeed)

"""

def prompt_engine(prompt, task):
    tokens_used = 0 
    temp_content =[]
    response = openai.chat.completions.create(
                model="gpt-4-1106-preview", 
                #model="gpt-3.5-turbo-1106", 
                messages=[
                    {
                    "role": "user",
                    "content": prompt
                    },
                    {
                    "role": "assistant",
                    "content": task
                    }
                ],
                temperature=1,
                max_tokens=4000,  # Adjust as needed
            )
    tokens_used += response.usage.total_tokens
    #Returned response whether it is a list, tuple or dictionary. A Youtube has been created to support this.
    temp_content = response.choices[0].message.content
    print("This is the returned result. This is the content:", temp_content)
    print("Cost of usage: ", tokens_used)
    return temp_content

# Setup openai parameters and returns the response
def generate_content(prompt, task, call_to_action): 
    contents = []
  
    
    try:
        #creates in range number of messages.
        for _ in range(30): 
            content = ""
            for attempt in range(5):  # Limit the number of attempts
                content = prompt_engine(prompt, task)
                if 100 <= len(content) <= 230:

                    break  # Exit the loop if content length
                print(len(content))

            #contents has all the social media content in a list
            content = content + " " + call_to_action # Return back the content
            contents.append(content)
    except Exception as e:
        print("There has been an error")
        contents = [str(e)]
    return contents

#Creates the streamlit and ask the user to enter the required information
def Social_Media_Generator():
    content_list = []
    max_char = int(46) #This is the CTA variable
    st.title("30 Day Twitter Content Planner")
    """
        Making it easier to create 30 days worth of social media content
    """
    task="You are the world's best social media content creator for twitter. Use the AIDA framework in producing the tweets. Just provide the response and nothing else. Dont repeat the question again and don't give links and don't confirm using the aida framework. Create a twitter post based on the following ensuring it is under 220 characters in total"
    company_name = st.text_area("What is the name of your company")
    company_description = st.text_area("Please tell us more about your company.")
    Client_benefits = st.text_area("What benefits does your product/service offer to clients")
    Tone = st.text_area("What is the tone of your message? i.e., inspirational, sales pitch, funny, formal.")
    call_to_action = st.text_area("Include a Call To Action or website link", max_chars=max_char)
     
    # Time input widget
    time_input = st.time_input("Select a time you will like to publish", datetime.time(12, 0))
    # Set a default date
    default_date = datetime.date.today()
    # Create a date input widget
    selected_date = st.date_input("Select a start date", default_date)

    #When the client press the 
    if st.button("Generate Content"):
        with st.spinner("Generating content- - The process can take up to 5 minutes..."):

            prompt = "company name: " + company_name + " What we do: " + company_description + " The benefits to clients are: " + Client_benefits + " The tone of the tweets: " +  Tone
            content_list = generate_content(prompt, task, call_to_action)   



            # Check if content_list is populated
            if content_list:
                # Create a list to hold the dates
                datetime_list = [(datetime.datetime.combine(selected_date, time_input) + datetime.timedelta(days=i)).replace(tzinfo=None) for i in range(len(content_list))]

                # Create a DataFrame
                df = pd.DataFrame({ 'postAtSpecificTime (YYYY-MM-DD HH:mm:ss)': datetime_list, 'content': content_list})        # Convert DataFrame to CSV
                csv = df.to_csv(index=False).encode('utf-8')
                b64 = base64.b64encode(csv).decode()

                # Create download button
                href = f'<a href="data:file/csv;base64,{b64}" download="social_media_content.csv">Download CSV file</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                # Handle the case where content_list is empty
                df = pd.DataFrame(columns=["Content"])
                st.write("No content generated.")
            
            # Display the DataFrame as a table
            st.table(df)


    return content_list
    
def main():
    passed_content = Social_Media_Generator()
    rssFeed(passed_content)
if  __name__ == "__main__":
    main()

