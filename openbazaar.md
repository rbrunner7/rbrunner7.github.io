# Implementing Monero Support for OpenBazaar: An Analysis

## Introduction

There is considerable interest to support the Monero cryptocurrency as an additonal trade currency in [OpenBazaar](https://openbazaar.com/). Check e.g. the posts and threads [here](https://old.reddit.com/r/OpenBazaar/comments/ahokfs/openbazaar_monero_integration/), [here](https://old.reddit.com/r/Monero/comments/a6snlg/openbazaar_xmr_support/), and [here](https://old.reddit.com/r/OpenBazaar/comments/acz3go/why_dont_you_accept_monero/).

End of January 2019 I (René Brunner, Monero dev *rbrunner7*) volunteered for the job of making a thorough analysis what that would mean and then submit a report detailing my findings to the OpenBazaar and Monero communities. I didn't consider myself to be a prime candidate to do so from a knowledge and experience point of view but it seemed nobody more qualified was at hand to do it, so I set out to work.

In the following I will write quite a lot about things that are difficult or even impossible right now. I don't do so because I have basically already given up or because I want to discourage anyone - that would be a misunderstanding that I hope to prevent with this statement right here. My aim is to enable a good understanding of the task at hand, which **is** difficult and challenging so anybody who starts to work on it will do so with the right expectations and the right mindset. I am convinced that in the world of IT projects an illusion lost ("It will be easy") is a big win.

## Currency Support in the Current Version of OpenBazaar

The release version of OpenBazaar that it current as of February 2019 supports the 4 cryptocurrencies Bitcoin (BTC), Bitcoin Cash (BCH, I would guess the "ABC" variant, not the "SV" variant), Litecoin (LTC) and Zcash (ZEC). Furthermore the work on [Ethereum and ERC20 token support](https://openbazaar.org/blog/why-we-are-integrating-ethereum-into-openbazaar/) is nearing completion and will probably go into one of the next releases.

The OpenBazaar client includes a simple but fully functional multi-currency wallet, i.e. a views where users can interactively manage funds in any supported currency (see e.g. chapter 4 [here](https://openbazaar.org/blog/8-reasons-why-openbazaar-20-is-better-than-10/) for some screenshots). For a buyer it's very easy to pay for their purchases out of this wallet (they are not forced to however).

The code to deal with the networks of these currencies to get balances, build and submit transactions etc. is in the OpenBazaar server; the multi-currency wallet merely calls into that server for any currency operations and so basically only manages the user interface.

Using those currencies is very easy for buyers. They do not have to install full nodes, and don't even have to find themselves something like "open nodes" or "remote nodes" to connect their wallets to: The OpenBazaar server contains so-called *SPV wallets* for all supported currencies where network access, at least from the user's perspective, "just works". (You can find some technical info about such SPV wallets e.g. [here](https://www.coindesk.com/spv-support-billion-bitcoin-users-sizing-scaling-claim)).

That everything "works out of the box" so easily for OpenBazaar users is certainly an important point when planning a Monero integration.

## Offline Selling

One issue that may look minor but actually seems to be quite important, and also will touch Monero integration as explained later, is the following: Does a vendor need to keep their OpenBazaar server running 24/7 connected to the net or not?

I found the following quite frank statement from Chris Pacia, one of the OpenBazaar lead devs, about the issue [here](https://np.reddit.com/r/OpenBazaar/comments/7q65y3/will_ob_implement_lighting_network_features/dstii7r/):

"One of primary pieces of feedback from OpenBazaar 1.0 was that vendors did not like having to run a server on their home computer 24/7 to make sales. ... For 2.0 we spent an enormous amount of time re-architecting OpenBazaar (and moved to IPFS) specifically to allow vendors to receive orders while they are offline."

It seems to make sense to me on a quite intuitive level: Imagine putting up something to sell on eBay and then having to keep your PC running constantly up to the time of the sale. I think such a requirement would be a hard sell to eBay users.

## Types of Payments in OpenBazaar

The OpenBazaar blog entry [Escrow Smart Contract Specification in OpenBazaar](https://openbazaar.org/blog/Escrow-Smart-Contract-Specification-in-OpenBazaar/) details the two types of payments that are used during the buy process (of which the second type has two subtypes) and the role multisig plays there.

If the buyer opts for moderation there will be a *moderated payment* which technically is based on 2/3 multisig: There are three authorized signers (the buyer, the vendor and the moderator), where any two signers are required to release any funds that were transferred into the 2/3 multisig address.

If the buyer trusts the vendor and opts to go without moderation, a so-called *direct payment* are used. There are two types depending on whether the vendor is online at the time the buyer wants to pay (*online direct payment*) or not (*offline payment*): If they are offline, 1/2 multisig is used where either the vendor can get the funds when they finally come back online, or the buyer can get the funds back should that never happen.

## Matching Orders and Payments

I hope I got the following correctly from my chat with one of the OpenBazaar devs:

Each order gets its own unique order id. The OpenBazaar servers of the buyer and the vendor can message each other over IPFS to inform about any new orders and their id. Each order also gets its own **unique** cryptocurrency address that the servers learn from those messages as well. For a moderated payment and for an offline payment it's the buyer which configures a new (multisig) address and tells it the vendor. For an online direct payment it's the vendor which hands a new (conventional) address to the buyer to pay into.

In all three cases the vendor then listens for an incoming transaction on the address belonging to the order. As it's unique it must be the buyer who made the transaction.

It seems that for some technical reasons that I don't fully understand Ethereum has a little twist here: Somehow the vendor is **not** able to see the buyer's transaction into the smart contract that governs all Ethereum-based OpenBazaar transactions based alone on the information that the buyer is able to give **before** they pay. Here one additional OpenBazaar server-to-server message is needed for everything to function correctly.

## Implementing New Currencies

Quite in general good multi-currency support seems to have been one of the most important goals when developing the 2.0 version of OpenBazaar, based on the experiences gained with the 1.x versions. New coins are welcome, under certain conditions, as outlined in the dev documentation [Creating an altcoin integration](https://github.com/OpenBazaar/openbazaar-go/blob/master/docs/altcoins.md). There is also a blog entry about this: [Freedom To Trade Means Freedom To Choose Currencies: The OpenBazaar Multiwallet](https://openbazaar.org/blog/Freedom-To-Trade-Means-Freedom-To-Choose-Currencies-The-OpenBazaar-Multiwallet/)

So I would say preconditions for integrating Monero into OpenBazaar look good.

## wallet.go: "Currency Drivers" for OpenBazaar

OpenBazaar defines an interface between any currency-specific code and the rest of the OpenBazaar server. The interface definition is contained in the repository [wallet-interface](https://github.com/OpenBazaar/wallet-interface).

Because the term *wallet* is somewhat over-used and ambiguous I use an other terminology in the following explanation: I compare this with device drivers in operating systems.

A *device driver* implements an interface defined by the OS describing something like an abstract device of some type, say a block storage device or a graphics card. Such interfaces develop over time, as the devices learn new things, and the device abstraction must be extended before the OS can use those new capabilities.

You could say that OpenBazaar uses *currency drivers* instead of device drivers, but the general approach is the same: The wallet UI in the OpenBazaar client and the OpenBazaar server work with some abstract coins, and those currency drivers implement the actual functionality which of course differs between coins to various degrees.

**The** central file here is [wallet.go](https://github.com/OpenBazaar/wallet-interface/blob/master/wallet.go) in the repository above: It defines the currency driver interface, the calls that a currency driver must support.

Currently there are four completed and released currency drivers implementing this interface, for the four already-mentioned coins BTC, BCH, LTC and ZEC. A fifth driver for Ethereum and ERC20 coins is nearly completed; it can be found in its own repository [here](https://github.com/OpenBazaar/go-ethwallet).

In my opinion the currency driver interface as defined by `wallet.go` is influenced by Bitcoin to quite some degree. For example check the method [GenerateMultisigScript](https://github.com/OpenBazaar/wallet-interface/blob/master/wallet.go#L181). Directly or indirectly it assumes a number of things about the coin's multisig capabilities: E.g. that something like a *redeem script* plays a role there, and that you can completely construct a multisig address in **one** step, given only a number of keys and a threshold to use, the number of required signers.

Personally, looking at this situation, I wonder why the DASH dev community did not yet write and contribute a currency driver for OpenBazaar: Given that DASH is in principle a BTC fork, a driver should not be hard to implement.

It's interesting to see how OpenBazaar implemented its Ethereum currency driver. They wrote a very [informative report](https://openbazaar.org/blog/Escrow-Smart-Contract-Specification-in-OpenBazaar/) about it. They implemented a *smart contract* in *Solidity* (source [here](https://github.com/OpenBazaar/smart-contracts/blob/master/contracts/escrow/Escrow_v1_0.sol)), and what is programmed there mimics in a number of aspects the way multisig works in Bitcoin and the abstraction of it defined by `wallet.go`.

Check e.g. the method [calculateRedeemScriptHash](https://github.com/OpenBazaar/smart-contracts/blob/master/contracts/escrow/Escrow_v1_0.sol#L396) which implements something that identifies a multisig "address" and its configuration through a hash just like a redeem script and its hash do in Bitcoin.

Through the magic of smart contracts it was finally possibly to "shoehorn" the quite un-Bitcoin-y Ethereum into something that can still implement the required currency driver interface `wallet.go`.

## Bitcoin Multisig

Compared with Monero multisig Bitcoin multisig is surprisingly simple. If you want to learn how **exactly** it works check e.g. [Bitcoin multisig the hard way](https://www.soroushjp.com/2014/12/20/bitcoin-multisig-the-hard-way-understanding-raw-multisignature-bitcoin-transactions/).

For the use within OpenBazaar and for a comparison with Monero multisig the following properties are important: If the buyer can obtain one public key from the vendor and another public key from the chosen moderator, they can then add a third public key and construct a 2/3 multisig address **all on their own**.

As I understand because of the use of [IPFS](https://en.wikipedia.org/wiki/InterPlanetary_File_System) the buyer can obtain those public keys even with the vendor and the moderator currently being offline. And note that a **single** such public key from the vendor can be used by any number of buyers / any number of purchases; only the buyer has to calculate a new key pair each time.

So this capability to construct 2/3 multisig addresses is an important part to achieve offline selling capability in the sense of chapter *Offline Selling* above.

Watching for transactions to a multisig address is simple, and each party can do that on their own. (If you don't understand why I stress that and say to yourself "Of course, how could it be otherwise?" wait until you have finished the following chapter about Monero multisig.)

Signing and submitting multisig transactions to the Bitcoin network is also simple, as there are no additional steps needed: All required parties sign, one party submits the transaction to the network, it gets mined, all parties note that and adjust balances on their own, finished.

## Monero Multisig

You can find details about constructing a Monero 2/3 multisig address and making transactions with it using Monero's own CLI ("command line interface") wallet e.g. [here](https://taiga.getmonero.org/project/rbrunner7-really-simple-multisig-transactions/wiki/23-multisig-in-cli-wallet).

An quite extensive article which also explains the handling plus some of the cryptographical background of Monero multisig, the "inner workings" so to say, can be found here: [Monero multisignatures explained](https://hackernoon.com/monero-multisignatures-explained-46b247b098a7)

The academic paper from the *Monero Research Lab* (abbreviated as *MRL*) with the full theory is this: [Thring Signatures and their Applications to Spender-Ambiguous Digital Currencies](https://eprint.iacr.org/2018/774.pdf)

Noteworthy regarding OpenBazaar are the following facts:

A Monero 2/3 multisig address can only be constructed with all 3 parties cooperating and exchanging key data with each other over **two** distinct rounds.

Personally I don't understand enough about the "theory" of Monero multisig to be able to explain **why** this is so, but in preparation of this report I got the explicit confirmation of somebody in the know: There is no easier way right now, certainly no **one-step** and **offline** process like with Bitcoin as described in chapter *Bitcoin Multisig* above, and no "Monero Multisig 2.0" on the horizon either that would make it one-step in the foreseeable future.

There is a second important issue: After receiving a funding transaction to the multisig address and after a multisig transaction was submitted to the network and mined, again the parties must cooperate and exchange data called *key images* with each other before they are able correctly interpret what happened and get into a state where they are able to spend what was received: They have to *sync the wallets*.

There are other restriction that you only notice if you look quite closely. If you do several transactions you have to execute them in order: It's strictly "Transact, sync, transact, sync, transact etc." For example you can't sign **two** transactions and send them both to another authorized signer to sign and submit both. More than one transaction "in transit" does not work.

One the one hand it may surprise how complicate things can become if you don't have a completely transparent blockchain like Bitcoin's, but a completely opaque one like Monero's, with senders hidden, receivers hidden, and even amounts hidden. On the other hand it may be impressive that multisig works at all under such conditions.

Finally a note about 1/2 multisig that is used in OpenBazaar for *offline payments* (see chapter *Types of Payments in OpenBazaar*): There is no such thing as 1/2 multisig in Monero. If you want to have an address where more than one person has complete control over it, simply send your private keys to all the persons in question - same effect, but completely outside the realm of "real" Monero multisig.

## Monero Wallets

This chapter is not about wallets in the sense of programs where users handle their "coins" and make payments, but about core wallet functionality: Scanning the blockchain for payments belonging to certain addresses, constructing transactions and submitting them to the network, and handling a data store with various things related to those addresses in it like cached transaction data or configuration info.

In Monero this is the job of a C++ class called `wallet2`. The source can be found [here](https://github.com/monero-project/monero/blob/master/src/wallet/wallet2.cpp). It's a massive and quite complex thing, with over 12,000 lines of code. I would estimate that's easily several times more code than is necessary to interact and transact with the Bitcoin network and handle a BTC wallet.

To my knowledge there never was a complete rewrite of `wallet2` within the Monero ecosystem. Even the three released smartphone wallets *Monerujo*, *Cake Wallet* and *X Wallet* have deep inside somewhere C++ based parts containing `wallet2`. *MyMonero* probably comes closest to a full alternative implementation, but even they "cheated" somewhat and compiled parts of the Monero C++ to JavaScript using [Emscripten](https://emscripten.org/).

And `wallet2` even continues to grow. Currently the implementation of a new feature called *multiuser transactions* or similar is under way.

Interestingly, there is project called [DERO](https://github.com/deroproject/derosuite) which started life as a code fork of Monero but was rewritten in Go from the ground up afterwards. I don't know their code, but there must be something like the `wallet2` class in there somewhere, written in Go of course. Could that be used for supporting Monero in OpenBazaar? I currently don't think so: On the one hand DERO uses a [Research License](https://github.com/deroproject/derosuite/blob/master/LICENSE) which restricts use of the code, and on the other hand the DERO and the Monero project are at best ignoring each other mostly.

With so many words I basically want to make clear: It's not realistic to include full Monero wallet functionality directly into OpenBazaar like it is done in all the other currency drivers: Too expensive, too much effort to implement. I believe there will be a requirement to run some additional binary alongside the OpenBazaar server where the real Monero functionality is based on `wallet2`, and some mechanism for the Monero currency driver to call into that.

## monero-wallet-rpc

Thankfully there is already something that implements a thin shell around `wallet2` and makes it accessible through RPC (remote procedure calls). It's a standard part of the Monero software distribution in the form of a stand-alone binary called `monero-wallet-rpc`. The code is [here](https://github.com/monero-project/monero/blob/master/src/wallet/wallet_rpc_server.cpp).

Somebody also wrote bindings to that interface in Go. The project can be found on GitHub [here](https://github.com/gabstv/go-monero). I tested that, and the basic functionality works, despite the fact that the code is not yet updated for the 0.13.0.x release of Monero, it's still on 0.11.0.0. I contacted the author, and he would welcome the use of his bindings within Monero for OpenBazaar and might even update the code.

So, as I see it, supporting Monero in OpenBazaar would include and would require to configure and run `monero-wallet-rpc` alongside the OpenBazaar server.

## Access to the Monero Network

Currently there are 3 established ways how to get access to the Monero network.

The safest and recommended way is running your own full node, i.e. running the Monero daemon binary `monerod` somewhere under your own control, using a complete and up-to-date copy of the Monero blockchain. Doing so is not that hard, but of course still requires some effort and storage room for the blockchain which is over 70 GB now. In the past some people found the initial blockchain download to be quite hard and time-consuming, and while that "experience" has been improved, it's still quite a hurdle, and of course for devices like smartphones running a full node right on the device is more or less out of question.

That's why so-called *remote nodes* have gained in popularity: You connect to a Monero node that some kind soul is running somewhere on the Internet for the benefit of people without own full nodes. Technically the interface between wallet and daemon used is exactly the same however. The most popular place to go for access to a remote node right now is probably [moneroworld.com](https://moneroworld.com/) where you get connected to a node randomly selected through some round-robbing mechanism.

This all is strictly volunteer-based and would probably get capacity problems pretty soon if too many people used it.

The third way is using a server based on the [MyMonero](https://mymonero.com/) technology. Here you hand over your *secret view key* to a special server which then connects to a Monero daemon, scans the blockchain on your behalf, and reports back the result to your wallet. This is a process which generates much less network traffic and needs less local computing power than having your standard wallet accessing a remote node. Details can be found e.g. starting on the [OpenMonero GitHub repository](https://github.com/moneroexamples/openmonero).

I haven't closely followed the development of the MyMonero project, but to my knowledge this third way of accessing the Monero network has not really taken off yet, lacking public servers available to connect to. Also, some people are not very comfortable handing over their secret view key to some remote server not under their control, although you can't possibly spend any coins with that key - you need the second key, the *secret spend key* to do so.

What does this mean for OpenBazaar and Monero? As I posit in the chapters *Monero Wallets* and *monero-wallet-rpc* that using `monero-wallet-rpc` is more or less set, it's either using a local Monero node together with that or connecting to a remote Monero node.

## An OpenBazaar "Currency Driver" for Monero

So, after so much information I can finally detail the conclusions I reached about what it would mean to implement a currency driver for Monero.

I will detail this for the three types of payments as listed in chapter *Types of Payments in OpenBazaar* because, maybe somewhat surprisingly, the issues and difficulties with Monero vary wildly between those types.

### Online Direct Payments

This type of payment is the easiest to implement. There is a feature in Monero called *subaddresses*: If you hold the keys of an address you can derive as many subaddresses as you want. I think for once this aspect of Monero works quite similarly to Bitcoin. So it's easy for the vendor to create a new subaddress for every trade and instruct the buyer to pay into that.

I wasn't yet able to go through `wallet.go` systematically and check every non-multisig-related method whether it can be implemented i.e. translated to remote calls to `monero-wallet-rpc`, but I am quite sure that this must be possible: The handling of simple direct transfers does not differ between Bitcoin and Monero, after all.

Maybe there will be a few cosmetic problems in the wallet UI because Monero addresses are so awfully long (95 characters). Monero's own GUI wallet solves such problems by showing only the start and the end of an address connected with dots to hint at the omitted part; maybe something similar can be done in the OpenBazaar wallet UI.

### Offline Payments

Unfortunately we run into some difficult issues with Monero here: As already mentioned in chapter *Monero Multisig* Monero doesn't support 1/2 multisig that OpenBazaar uses for this type of payment, and even if it did it would be subject to the difficulties outlined in the next chapter *Moderated Payments*.

With the help of the vendor's private view key the buyer would be able to derive a new subaddress from the vendor's main Monero address on its own and could send that with a server-to-server message to the vendor so the "unique address for each trade" requirement would be met (see chapter *Matching Orders and Payments*), but making the private view key available to all buyers is probably unacceptable for vendors.

Until now the "order-to-payment-matching" task that currency exchanges in particular have to carry out for incoming Monero transactions is usually done by using a *payment id*, a unique id that the sender can attach to a Monero transaction and that the receiver can see. This is no solution for OpenBazaar however because payment ids are "on their way out" and will soon not be available anymore, for several reasons not worth detailing here. If interested check the dev community discussion [here](https://github.com/monero-project/meta/issues/299).

So what is left? Monero knows *payment proofs*, where the sender of a transaction constructs a cryptographically sound proof about the origin of the transaction that the receiver can verify. Details are e.g. [here](https://ww.getmonero.org/resources/user-guides/prove-payment.html) and [here](https://monero.stackexchange.com/questions/8122/what-is-the-spendproofv1-or-outproofv1-in-the-details-of-a-sent-transa).

With those all buyers would send their XMR to the **same** main address of the vendor, but would additionally send payment proofs using server-to-server messages so that the vendor knows which payment comes from which buyer and can be sure that those buyers tell the truth and do not only pretend to have made a payment.

Such an additional payment-related message already has something like a precedent in connection with Ethereum-based payments as mentioned in chapter *Matching Orders and Payments* and thus is probably not too bad, but I am not sure about the consequences of breaking the "unique address for each trade" rule.

So, to summarize, I think we could get offline payments to work for Monero, but only with quite some effort.

### Moderated Payments

Supporting moderated payments implies supporting Monero 2/3 multisig in OpenBazaar.

I came to the conclusion that the current OpenBazaar "driver model" as defined by `wallet.go` (see chapter *wallet.go: "Currency Drivers" for OpenBazaar*) does not allow to implement Monero multisig. Prime example: The method `GenerateMultisigScript` has the job to create a multisig address in a single step. This is **impossible** for Monero, as the chapter *Monero Multisig* spells out, in Monero this needs **two** steps.

And it won't be enough to simply split this method into two, e.g. `StartGenerateMultisigScript` and `FinalizeMultisigScript`, to accomodate this. In Monero you need communication between all three authorized signers (buyer, vendor and moderator) over two rounds which I would say fully goes against the "spirit" of `GenerateMultisigScript` and of course collides with the goal of allowing people to trade and prepare trades offline (see chapter *Offline Selling*). Furthermore moderators may not like that because it means they cannot wait to enter the picture until a disputed case happens but must have at least keep an automated system running all the time that cooperates for building the wallets.

As I see it, supporting Monero multisig would need a substantial redesign of the multicurrency support in OpenBazaar and lifting the driver interface `wallet.go` to a considerably more abstract and also much less "Bitcoin-y" level. As this interface was only introduced quite recently and is very important to the OpenBazaar server I imagine such a proposal could be quite "hard to sell".

I think even the user interface for handling wallets by the OpenBazaar users would need additions, you probably won't be able to hide everything that has to happen deep within the OpenBazaar server: Often your wallet will wait for some information arriving from another party, and you need some info display what has arrived already and what is still missing. Check the many commands my own [Multisig Messaging System](https://rbrunner7.github.io/mms_full_manual.html) added to the Monero CLI wallet to make the exchange of multisig-related data between wallets really transparent for the user and robust in handling.

This all **can** be done and would probably be a very interesting and challenging project, but it would need a concerted and substantial joint effort of the Monero and the OpenBaazar dev communities to pull it off.

## Politics

So far I see two questions surrounding Monero in OpenBazaar that have less to do with technicals and more with what you could call *politics*.

### Monero: "Official" OpenBazaar Currency or Not?

One question is: Suppose a first Monero "currency driver" for OpenBazaar is implemented. What will be the status of that code? Will it be integral part of the official OpenBazaar package from OB1, so a user simply downloads OpenBazaar, installs it and uses XMR as a fifth or sixth "natively" / "officially" supported cryptocurrency? Or will it be more complicated because the code does **not** have such a status? In theory it could get as hard as having to compile OpenBazaar oneself e.g. using a special switch, or even having to use a Monero-specific OpenBazaar fork.

Why is this all even an issue? As far as I understand from my chat with one of OB1's devs, Mike Greenberg, seen from the viewpoint of OB1 tricky issues can arise concerning currency support. For example there could be more than one implementation of support for a particular coin, from several devs. Is OB1 capable to choose a particular one as the "official" one, leaving the others aside? Would it even be up to OB1 to decide something like that and favor one over the others?

I can also imagine problems with know-how: The more currencies are supported the higher the chance that some original outside devs stop to support some code, which leaves OB1 with basically two choices, both not very attractive: Drop support for a currency although it's one of the *officially supported* ones until that point, or spend company money to pick up and support the code on their own after acquiring the necessary know-how.

Greenberg mentioned the idea of implementing something like a *currency plugin system* for OpenBazaar, where the plugins would probably be separate units of executable code, like DLLs in Windows or Linux. The users would be able to freely decide on their own which plugins to use and could swap them in and out of OpenBazaar using easy configuration options. If there were several XMR plugins it would be, quite naturally, the user's choice which one to use. And also it would be pretty clear that the burden to keep a plugin up-to-date and working e.g. after a hardfork of the supported currency is on the developer of the plugin, not on OB1.

Alas, it seems such a plugin system is hardly on the drawing board yet, much less being worked on already, so it's doubtful whether it would make sense for Monero to wait until it's available.

Personally I currently doubt that a merely "unofficial" support of Monero would have a reasonable chance of success: I fear that if both vendors and buyers have to jump through some hoops first before they can trade using XMR, how many vendors and buyers will find each other at all this way?

But of course I readily acknowledge that this is a complex and maybe thorny question that needs a serious discussion between all involved parties.

### Possible Lack of Monero Multisig Support Acceptable?

A second somewhat political question is how to react if closer investigations confirm that supporting Monero multisig in OpenBazaar is out of reach at least for a considerable time, worst case even "forever". Personally, after my analysis and the unearthed problems documented in chapter *Moderated Payments*, I see a higher probability of such an outcome than I would like.

I refer to the OpenBazaar document [Creating an altcoin integration](https://github.com/OpenBazaar/openbazaar-go/blob/master/docs/altcoins.md), chapter *Cryptocurrency support in reference implementations*:

"A proposed integration must meet the following conditions: 1. The coin must support multisig."

This requirement is certainly reasonable, as seamless support for moderated payments using fully automated 2/3 multisig is an important part of the OpenBazaar UX. But anyway, if Monero multisig was out of reach for objective technical reasons that nobody can be blamed for, what would be the "lesser evil": Forgetting Monero, or supporting it without multisig support?

I think like the first question about the status of Monero among OpenBazaar's supported currencies in general this one here certainly needs a good discussion.

