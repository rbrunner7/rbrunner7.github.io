# "No Wallet Left Behind" - Make Sure Our Wallets Survive the Fork to Monero 2.0

## The Short Version

If things proceed as currently planned Monero will, maybe sometime in 2023 or 2024, hardfork to a second-generation protocol called *Seraphis* and a new addressing scheme called *Jamtis*. These changes are so extensive that you could very well call the resulting cryptocurrency *Monero 2.0*.

Monero wallets of all types - desktop, smartphone, web - will need larger functional / UI changes to fully support this.

The main problem for wallets however, as I see it: The Monero core software will probably offer a quite different programming interface / API that Monero wallets must use in order to continue to function. And this in turn will require an extensive refactoring of the code of the wallets, regardless of the programming language used and the OS they run on. This is difficult, expensive and can take a lot of time.

Personally I see a real danger that at least some important and widely used Monero wallets won't be ready for the hardfork, and that we might even loose wallets because the challenge will be too great for their authors and they will be forced to discontinue their apps.

I propose to start a dedicated effort to prevent such a very unfortunate outcome by working out a clear and well-documented migration path for wallets towards Seraphis and Jamtis, and start this effort not with the hardfork already looming at the horizon mere months away, but **right now**.

This effort will probably be as much about project management as it will be about technology and programming interfaces.

## Background

Work is well under way to implement something you could call a "second-generation protocol" for Monero called *Seraphis*. You can find details on the author @UkoeHB 's GitHub [here](https://github.com/UkoeHB/Seraphis). In parallel @tevador designs a new addressing and wallet tiers scheme to be used with Seraphis called *Jamtis* that is currently documented and discussed [here](https://gist.github.com/tevador/50160d160d24cfc6c52ae02eb3d17024).

The changes compared with the current Monero protocol and addressing scheme will be extensive: Better privacy through much larger rings, with a quite different structure of transactions as recorded in the blockchain, migration to new address formats (every wallet will get new addresses), wallet types (going far beyond merely 2 wallet types "full" and "view-only"), seed format (16 words instead of 25), and more. In a recent IRC chat UkoeHB called this half-jokingly *Monero 2.0* which personally I find spot-on and use here in earnest to make clear the magnitude of the changes.

As I see it Seraphis and Jamtis bring Monero forward enormously, but at the same their introduction is a monumental endeavor in every respect, and not only technically difficult, but also a formidable project management challenge for a team of open-source devs as large and as diverse as Monero's.

If we stay on this course I would roughly estimate that the hardfork to Seraphis and Jamtis could take place in 2023 or 2024.

## Monero's Wallet "API"

There is a large and complicated C++ class named `Wallet2` that is an integral part of the Monero core code base. You find its header file [here](https://github.com/monero-project/monero/blob/master/src/wallet/wallet2.h).

You could say that this class is the "center of the universe" they revolve around as far as most Monero "consumer" wallet apps are concerned. Internally the typical wallet app ends up calling methods of this class extensively to manage Monero wallets, either directly or through some thin layer like `wallet.h` that the GUI wallet uses (source is [here](https://github.com/monero-project/monero/blob/master/src/wallet/api/wallet.h)).

If you look at this class as Monero's wallet handling API, as far as I know this interface has stayed remarkably stable since Monero's birth in 2014. It has certainly grown with the introduction of multisig, RingCT, subaddresses and other things, but was probably never fully "overturned"- a fortunate fact for Monero wallet apps because they could count on a solid fundament over many years.

## The Problem

During the already-mentioned chat about Seraphis and Jamtis wallets on IRC the following problem suddenly dawned on me: It will probably not be possible in a sensible way to merely somewhat extend `wallet2.h` as an API once more to accomodate Seraphis and Jamtis. Right now the functional changes seem simply too great to me for that, and IMHO this class is not particularly well designed to serve as such an important API anway, and it has a quite low level of abstraction which makes it vulnerable to any larger functional changes.

Anyway, while the header file might still look quite reasonable, `wallet2.cpp` is a gigantic complicated mass of C++ code (its over 14,000 LOCs are [here](https://github.com/monero-project/monero/blob/master/src/wallet/wallet2.cpp)) that cries out for refactoring for years already, but so far no Monero dev really dared to take on the challenge, because of the amount of work involved and the very central role of the class for the whole Monero software universe already described.

Somehow stuffing Seraphis wallet handling and Jamtis address management into `wallet2` would probably be sheer madness from an engineering point of view, and UkoeHB has, rightfully so IMHO, already made clear that he has no intention whatsoever to even try.

If you followed me so far maybe you start to see the same problem I see: If this API falls away and gets replaced by something new and considerably different the very fundament most Monero wallet apps rely on will get pulled out from under their feet. This will require large and time-consuming changes in their codebase.

And this in turn will lead to a serious project management problem: How can we make it possible for wallet app authors to start early enough with adapting their code to be ready for the hardfork to Seraphis and Jamtis in time?

If we are not careful here we might end up with a situation where on the day of the hardfork only the CLI wallet is fully functional, the GUI wallet is still on its way, and it's unclear when smartphone wallets like Monerujo and Cake Wallet will be functional again thanks to updates. Or, the other way round, we might have to postpone the hardfork many months, maybe even more than once, despite everything being ready in the core software already.

## Proposal

I propose to work out a clear and well-documented migration path for Monero wallet apps towards Seraphis and Jamtis, and start with this work more or less immediately.

How could that path look? In a very first round of brainstorming I had the following idea that may be worth discussing further after starting a corresponding project:

Maybe it's possible to define a new API - let's call it `wallet3` as a working title - that is abstract and flexible enough to be suitable for Seraphis and Jamtis on the one hand, but on the other hand can be used to handle current Monero wallets as well. In this scenario the first implementation of `wallet3` would be a reasonably thin layer above `wallet2`, with that former class still doing almost all the "heavy lifting".

Advantage: With this API available e.g. at the end of this year 2022, wallet app authors could already start migrating during 2023 and then switch to it well ahead of the Seraphis and Jamtis hardfork. The final switch to the new technologies would be relatively simple and could avoid painful deadline troubles.

Another thought that crossed my mind was deprecating any direct "binary" interfaces outright and starting to fully rely on RPC. There is already now an almost fully feature-complete RPC wallet interface - the header file describing it is [here](https://github.com/monero-project/monero/blob/master/src/rpc/core_rpc_server_commands_defs.h) - and I think this interface has a much better chance of getting successfully extended to accomodate Seraphis and Jamtis than `wallet2.h`.

What I don't know however right now is how difficult it is to put smartphone wallets on such an RPC-based fundament.

It's worth to mention here that Monero dev @woodser has defined a new and clean wallet API quite a while ago already and implemented it in C++, Java and JavaScript. The design is documented [here](https://moneroecosystem.org/monero-java/monero-spec.pdf), its C++ implementation is [here](https://github.com/monero-ecosystem/monero-cpp). It's only for the current Monero technology of course, but maybe it could serve as a good starting point for `wallet3`.

## Requirements for Success

To sucessfully pull off a "Monero wallet migration" project like I decribe it here two things are important in my opinion:

People are needed to work on it, preferably people with knowledge already about the architecture and structure of the Monero codebase, and ideally some experience in API design plus project management on top of it.

But secondly the Monero dev community and the broader Monero ecosystem must come to stand behind the worked-out strategy and accept it as the way forward. Wallet app authors must come around to trust it enough to bank the future of their apps on the resulting migration strategy and API, based on at least a "loose consensus" that it's solid and suitable.

Regardless of quality it's quite easy to ignore to death something like that and turn it into a failure. Build it, and nobody comes, for many possible reasons: because of "I don't care enough", because of "Nobody ever asked me", because of "Not Invented Here", because of "I can do better", or even "I just don't like the people in this workgroup".

Of course I am well aware that you can't force anything here; acceptance must come as a natural consequence of the quality of the work and the trust earned by the devs involved.

