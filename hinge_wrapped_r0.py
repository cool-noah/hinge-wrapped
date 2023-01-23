#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
from datetime import datetime
import pandas as pd
import numpy as np
import calendar
import plotly.express as px


# In[2]:


pd.set_option('display.max_columns', None) #Showing all columns for any pandas dataframe 
pd.set_option('display.max_rows', None) #Showing all rows for any pandas dataframe 


# In[3]:


input_file = r'C:\Users\nlevin\DS_Portfolio\hinge\hingedata\matches_LVR.json'


# In[4]:


with open(input_file) as f:
    data = json.load(f)


# In[5]:


#Getting Data From The Chats 

chat_length_list = []
chat_text = []
like_time = []
match_time = []
chat_time = []

del data[3009].get('chats')[58]

for x in range(len(data)):
    if 'like' in data[x]:
        time_of_like = data[x].get('like')[0]['timestamp']
        time_of_like = time_of_like.split("T")[0]+" "+time_of_like.split("T")[1].split('.')[0]
        time_of_like = datetime.strptime(time_of_like,'%Y-%m-%d %H:%M:%S')
        like_time.append(time_of_like)
        
    if 'match' in data[x]:
        time_of_match = data[x].get('match')[0]['timestamp']
        time_of_match = time_of_match.split("T")[0]+" "+time_of_match.split("T")[1].split('.')[0]
        time_of_match = datetime.strptime(time_of_match,'%Y-%m-%d %H:%M:%S')
        match_time.append(time_of_match)

    if 'chats' in data[x]:
        chat_length = len(data[x].get('chats'))
        chat_length_list.append(chat_length)
        for i in range(len(data[x].get('chats'))):
            text = data[x].get('chats')[i]['body']
            chat_text.append(text)
            chat_timestamp = data[x].get('chats')[i].get('timestamp')
            chat_timestamp = chat_timestamp.split("T")[0]+" "+chat_timestamp.split("T")[1].split('.')[0]
            chat_timestamp = datetime.strptime(chat_timestamp,'%Y-%m-%d %H:%M:%S')
            chat_time.append(chat_timestamp)


# In[6]:


#Make a list of all words used 

words = []

for sentence in chat_text:
    if type(sentence) != int:
        sentence = sentence.split()
        for word in sentence:
            words.append(word)


# In[7]:


#Counting Likes, Matches, Rejections, and ghosts
rejected = 0
likes = 0
matches = 0
chats = 0
u_ghosted = 0
unrequited_love = 0
they_dunk = 0
they_ghosted = 0
u_dunk = 0
total_interactions = 0


# In[8]:


#code for counting
for blob in data:
    interactions = list(blob.keys())
    first_interaction = interactions[0]
    if len(interactions) > 1:
        second_interaction = interactions[1]
    else:
        second_interaction = 'noop'
    total_interactions += 1
    if first_interaction == 'block':
        rejected += 1
    elif first_interaction == 'like':
        likes += 1
        if second_interaction == 'match':
            matches += 1
            u_ghosted += 1
            u_dunk +=1
    elif first_interaction == 'match':
        matches += 1
        they_dunk += 1
        they_ghosted += 1
    elif first_interaction == 'chats':
        chats += 1
        if second_interaction == 'like':
            likes += 1
            matches += 1
            u_dunk +=1
        elif second_interaction == 'match':
            matches += 1
            they_dunk += 1


# In[9]:


match = pd.DataFrame(match_time, columns = ['time'])
like = pd.DataFrame(like_time, columns = ['time'])
chat_time = pd.DataFrame(chat_time, columns = ['time'])
chat_length = pd.DataFrame(chat_length_list, columns = ['length'])
word = pd.DataFrame(words, columns = ['word'])


# In[10]:


time_dfs = [match, like, chat_time]


# In[11]:


for df in time_dfs:
    df['year'] = df['time'].dt.year
    df['month'] = df['time'].dt.month
    df['day'] = df['time'].dt.day
    df['hour']= df['time'].dt.hour
    df['date'] = df['time'].dt.date
    df['weekday'] = df['time'].dt.weekday.apply(lambda x: calendar.day_name[x])


# In[12]:


#Analyzing maximums
max_time = chat_time['hour'].value_counts().idxmax()
if max_time < 12:
    AM_PM = 'AM'
else:
    AM_PM = 'PM'
max_day = match['weekday'].value_counts().idxmax()
most_matches = match['date'].value_counts().idxmax()


# In[13]:


match_gb = match.groupby('date')[['time']].count().reset_index()
chat_gb = chat_time.groupby('date')[['time']].count().reset_index()
like_gb = like.groupby('date')[['time']].count().reset_index()


# In[14]:


chat_gb['date'] = chat_gb['date'].astype('datetime64[ns]')
match_gb['date'] = match_gb['date'].astype('datetime64[ns]')
like_gb['date'] = like_gb['date'].astype('datetime64[ns]')


# In[15]:


from plotly_calplot import calplot


# In[34]:


fig1 = calplot(chat_gb, x="date", y='time', colorscale = 'blues')
#fig1.show()


# In[31]:


fig2 = calplot(match_gb, x="date", y='time',colorscale = 'blues')
#fig2.show()


# In[32]:


fig3 = calplot(like_gb, x="date", y='time',colorscale = 'blues')
#fig3.show()


# In[19]:


fig4 = px.bar(match.groupby(by = 'weekday')['date'].count().reset_index(), x = 'weekday', y='date', template = 'plotly_white',
             category_orders = {'weekday':['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']})
fig4.update_yaxes(title = 'Matches')


# In[20]:


fig5 = px.bar(chat_time.groupby(by = 'weekday')['date'].count().reset_index(), x = 'weekday', y='date', template = 'plotly_white',
             category_orders = {'weekday':['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']})
fig5.update_yaxes(title = 'Messages Sent')


# In[21]:


fig6 = px.bar(chat_time.groupby(by = 'hour')['date'].count().reset_index(), x = 'hour', y='date', template = 'plotly_white')
fig6.update_yaxes(title = 'Messages Sent')


# In[22]:


#Word Analysis
def word_in_list(test_word, word_list):
    if test_word in word_list:
        val = words.count(test_word)
        if val == 1:
            return 'You have used the word '+str(test_word)+' one time when talking to your matches'
        else:
            return 'You have used the word '+str(test_word)+' '+str(val)+' times when talking to your matches'
    else:
        return 'You have not used the word '+str(test_word)+' in a hinge conversation. Try it out!'


# In[23]:


word_in_list('penis',words)


# In[24]:


total_messages = len(chat_text)
total_words = len(word['word'].unique())


# In[25]:


word_count = word.value_counts()
top_ten = word.value_counts().head(10)


# In[26]:


once = word_count[word_count == 1]

once_list = list(once.index.values)


# In[27]:


#Number Strings
tot_string = "You've interacted with " + str(total_interactions) + " people on Hinge. That's a lot of thumb movement for ya!! \n"
rej_string = "You stone cold FOX! You've rejected " + str(rejected) + " people (ouch) \nYou match with " + str(round(matches/total_interactions * 100, 2)) + "% of profiles you see on Hinge.\n"
u_ghost_string = "Is it spooky SZN? You've ghosted at MOST " + str(u_ghosted) + " people \n"


# In[28]:


#Word Strings
msg_string = 'Tommy texter alert! You sent '+str(total_messages)+' messages this year\n'
word_string = 'Are you THE William Shakespeare?! You used ' + str(total_words)+ ' different words!\n'
top_word_string = 'The words you used most were ' + str(top_ten.index[0][0])+', ' +str(top_ten.index[1][0])+ ',and '+str(top_ten.index[2][0])+'. Maybe this is the year you learn some better words\n'


# In[29]:


#Max Strings
max_time_string = "Are you Harry Styles? Because SOMEONES been doing some late night talking. You sent most of your messages at " + str(max_time)+ ' ' + str(AM_PM)
max_day_string = 'Another thing you and Garfield have in common - and it aint lasanga. Your most commont day for getting matches is ' + str(max_day)
max_matches_string = 'This was either your happiest or saddest day. The day you most match with people was '+str(most_matches)


# In[37]:


import streamlit as st


# In[38]:
st.markdown("<h1 style='text-align: center; color: black;'>Hinge Wrapped </h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: grey;'> Let's take a deep dive into your year of dating </h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.header(tot_string)
with col2:
    st.header(rej_string)


# In[ ]:





# In[ ]:
