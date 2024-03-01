
<p align="center">
<img src="https://private-user-images.githubusercontent.com/43605638/305680763-c9767378-7d34-4e8e-a348-04c579d288d9.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MDgyMjMzNTQsIm5iZiI6MTcwODIyMzA1NCwicGF0aCI6Ii80MzYwNTYzOC8zMDU2ODA3NjMtYzk3NjczNzgtN2QzNC00ZThlLWEzNDgtMDRjNTc5ZDI4OGQ5LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwMjE4VDAyMjQxNFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWNjNjkyMjdhZTg1ZDEzZjk5ZTk1N2I5M2NlNWUyMWExYzdjYmQxZjI5MzE1YmQ1MDg5YWM5NjlmODk2YTc5OWYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.UwKKfFSMs962M2n46bibQO4XzGl578WZHY3ZKo8ruwM" width="100" height="100" align="right-center">
<h1 align="center"> KATABASE
</p>

Katabase is used to list artists, albums and songs released by K-pop artists by year.


## Using this script
Windows users: &nbsp;
After cloning this repository, add your YouTube API key to config.json (located under the "main" folder).


Run "katabase.bat" and follow the on screen instructions. See "Creating a YouTube API key" further down the page if you require one.


## Features
NOTE: This project uses KPOPPING.COM to find the information below. This script compiles the information from KPOPPING.
- List all artists, albums and songs released on a specified year
- List whether song has a music video, dance practice, choreography, studio choom etc (please submit an issue to request more)
- Verify the channel that has uploaded the above videos to ensure no "Fanmade" content is marked down as a music video etc.


## Creating a YouTube API key 

You can follow the instructions below, or follow this link: https://developers.google.com/youtube/v3/getting-started - you will **not** need to setup oAuth. This project only requires the API key.

This key only needs to be able to search YouTube and receive a response with the search data.

Go to Google Cloud (https://console.cloud.google.com/) and create an account if required, then create a new project. I have called mine KATABASE. 

Once the project is created, head to APIs and services and go to "Library" and search for "YouTube Data API v3" and select the result. Click the "ENABLE" button to activate this API.

Next, click the Google Cloud logo to head back to the main page, and once again head to APIs and services.

YouTube Data API v3 will be listed at the bottom of this page now.

On the left navigation menu, click "Credentials" and on the new page click "+ CREATE CREDENTIALS" and select "API key"

Copy the key where it says "Your API key" - this is your API key. It will look something like "AIzaSyBsjG2HN2_jubAR6GHl_IwK5G2-QF3HL6w" 

You can now add this to config.json, replacing "your_api_key".

IF POSSIBLE, it is recommended to restrict your API key to your IP address. This is only really viable if your ISP has granted you a static IP address. To restrict this, on the Credentials page click the 3 vertical elipses under "Actions" and select "Edit API key". Under "Set an application restriction" select "IP addresses" and add your IP address under "IP address restrictions". Ensure "Don't restrict key" is enabled - do not restrict the key here. Click SAVE.

If you cannot restrict your API key this is no problem, this is just to avoid someone else using your API key if it is found.
