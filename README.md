# ThaiAntiFakeNewsBot

A [Line](http://line.me/) chatbot that takes Thai news from users and attempts to label it as fake, real, distorted, or unverified by cross-checking with [Anti-Fake News Center Thailand](http://antifakenewscenter.com) database. Rather than being specific to Thai language, it is tailored to Thai news in the sense that it only relies on the website mentioned above as a reliable source of veracity labels. To make it clear, I'm a mere student developer and have no relation to the website creator or the organization behind it whatsoever.

The chatbot was written in Python and deployed through Heroku: [https://thai-fake-news.herokuapp.com](https://thai-fake-news.herokuapp.com/). You can find the QR code and Line ID to add our chatbot as a friend and try talking to it.

I'm planning to further improve this bot by adding some sort of a probabillistic (likely machine learning-based) fake news predictor so that would be able to predict truthfulness of unseen, unverified news. The biggest challenge are that there isn't really a high-quality fake news dataset in Thai language and I'm reluctant to use translation back and forth. However, one way or another, I plan to keep pushing forward with this big additional feature.

*Update: I tried to deploy a neural fake news classifier model to cover the "not found in database" cases, but the sizes of the libraries, the models (tokenizer, feature extractor, and classifier), and the memory required during runtime appears to exceed the 500MB limit imposed by the free Heroku. Thus, the system is currently down. I'm still deciding whether to try to fix it or revert to the previous version.*
