# ThaiAntiFakeNewsBot

## How It Works

A [Line](http://line.me/) chatbot that takes Thai news from users and attempts to label it as fake, real, distorted, or unverified by cross-checking with [Anti-Fake News Center Thailand](http://antifakenewscenter.com) database. Rather than being specific to Thai language, it is tailored to Thai news in the sense that it only relies on the website mentioned above as a reliable source of veracity labels. To make it clear, I'm a mere student developer and have no relation to the website creator or the organization behind it whatsoever.

The chatbot was written in Python and deployed through Heroku: [https://thai-fake-news.herokuapp.com](https://thai-fake-news.herokuapp.com/). You can find the QR code and Line ID to add our chatbot as a friend and try talking to it.

Usage Examples:
<img src="./templates/img1.png" width="45%"/> <img src="./templates/img2.png" width="45%"/>
<img src="./templates/img3.png" width="45%"/> <img src="./templates/img4.png" width="45%"/>

# What's Going On Inside

Basically what the program does right now is performing a Google search on the user input, retrieving a returned antifakenewscenter.com page if there is, and detecting relevant information (its vericity label, date confirmed, and the agency issuing it) to present back to the user. If there is none, the current version presents the first page from another website, but with a warning that it _unverified_ source. There are also internal ad-hoc algorithms implemented to try to check whether the retrieved page actually addresses the veracity of the user-inputted news.

I'm hoping to further improve this bot by adding some sort of a probabillistic (likely machine learning-based) fake news predictor so that would be able to predict truthfulness of unseen, unverified news. I have already tried to deploy a neural fake news classifier model to cover these cases, but the sizes of the libraries, the models (tokenizer, feature extractor, and classifier), and the memory required during runtime combined far exceed the 500MB limit imposed by the free Heroku. Thus, I have reverted it back to the version without such _intelligence_.
