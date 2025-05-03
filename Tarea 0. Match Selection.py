#!/usr/bin/env python
# coding: utf-8

# # Tarea 1. Mapa de tiros

# In[2]:


pip install statsbombpy


# In[3]:


from statsbombpy import sb


# In[4]:


sb.competitions()


# In[5]:


sb.matches(competition_id=16, season_id=1)


# In[6]:


events = sb.events(match_id=18245)


# In[7]:


events


# In[15]:


events.columns


# In[ ]:




