# A motion for implementing multiuser transactions and keeping them working long-time

What we call here *multiuser transactions* are transactions that contain outputs from more than one user, e.g. transactions that contain outputs from both Alice and Bob. Currently the functionality to build such transactions is not available in the Monero release code. 

We would like to motion for two things:

First, implement multiuser transactions and make them available as integral part of some of the next larger Monero releases, or with the hardfork that follows their implementation if necessary.

Second, commit to treating multiuser transactions as a feature that Monero will keep available long-term if reasonably possible. This means taking care that some form of them continues to work even after a switch away from current RingCT to a different protocol like Triptych.

Such transactions can serve as a "building block" of trade protocols for marketplaces that work with moderation in one form or another, like e.g. Bisq and OpenBazaar, using the rather useful form of coordination they make possible: Alice and Bob can be sure that both their funds will move **at the same time**, or not at all if nobody submits the transaction.

Marketplaces, decentralized exchanges and similar services may turn out to be very important parts of the future cryptocurrency ecosystem. With multisuser transactions as a reliable tool in Monero's "toolbox", assured to be available long-term, at least some of those services could run with Monero instead of Bitcoin or Ethereum as their foundation.

An initiative to make them available could profit from significant work already done in this area:

Core dev "moneromooo" implemented a multiuser transaction scheme called *MoJoin* (or something very similar) during spring 2019, until near completion it seems. See [this commit](https://github.com/moneromooo-monero/bitmonero/commit/746824408715ea3e623f9818d6bccb455fe8df7a) on their own GitHub repository.

Recently "koe" / "UkoeHB" proposed an improved scheme called *TxTangle* in chapter 11 of the second edition of *Zero to Monero* (current draft [see here](https://www.pdf-archive.com/2020/03/04/zerotomoneromaster-v1-1-0/zerotomoneromaster-v1-1-0.pdf)).

We are aware that some tangible drawbacks of the *MoJoin* scheme are known. We understood that making something like *CoinJoins*, i.e. joining the outputs of many people, are problematic, because those people will get to know who joins and contributes which outputs. It may also be possible to find out for outsiders with reasonable computational effort how many people participated, and how the outputs group.

As far as we learned it were these drawbacks that lead to the decision to stop working on the implementation.

Basically, we propose here to come back to this decision and re-evaluate. We have the opinion that even taking those problems into account enough benefits are left to make it worthwhile to make them available.

Maybe further investigations will show anyway that improved schemes avoiding at least some drawbacks like *TxTangle* are possible and indeed implementable with reasonable effort. Or that we only have to live with the problems until some sort of "next-generation protocol" enters service, with improved possibilities.

It may also depend how the feature gets implemented: Maybe only make it available predominantly for programmers, but not for the broad public in the CLI and the GUI wallets, avoiding people using it under wrong assumptions and not being aware about certain limitations and dangers for their privacy.

