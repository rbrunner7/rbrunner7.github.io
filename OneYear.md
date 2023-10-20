# Seraphis wallet development, 1 year report

TL;DR: A group of Monero devs is busy implementing "next generation" technologies for Monero called *Seraphis* and *Jamtis* that will bring solid improvements. After about 1 year passed since project start they did not yet get very far unfortunately but do have some interesting results to show, and speed will likely pick up considerably soon. Still, the corresponding hardfork is years out, and even the design of those technologies is not yet fully settled.

-------------

Next month it will be 1 year that a number of Monero devs formed something like a workgroup with the goal to develop a wallet for the upcoming Seraphis and Jamtis based Monero and I took on the job to care about the project management side. It's therefore a good time for a report about what happened so far.

You find general info about Seraphis, Jamtis and the workgroup [here](https://github.com/seraphis-migration/strategy/wiki/Seraphis-Wallet-Workgroup) on our wiki. The [Seraphis and Jamtis FAQ](https://github.com/seraphis-migration/strategy/wiki/Seraphis-and-Jamtis-FAQ) linked there may be especially useful.

We do not build a new wallet *app*, like Cake Wallet or Monerujo are wallet apps. We build a new component within the Monero core code that most of those apps will rely on internally once reworked for Seraphis. For lack of a good and unambiguous term we also call that component *wallet*.

I admit right away that we don't yet have many hard results to show, i.e. very little actual reviewed code that has a chance to become part of the final Monero software, and no prototype of any sort yet, despite the almost full year that passed.

Personally, I have mixed feelings about that but wouldn't call it an outright failure. I see several factors that resulted in this still modest result.

When UkoeHB, the designer / inventor of Seraphis, set out about 2 years ago to implement Seraphis and Jamtis as designed by Tevador, the idea was that he would crown his dev work with a prototype of a wallet that we other devs would then flesh out and improve until it reached production quality and finally became ready for a hardfork.

Unfortunately building a wallet prototype turned out to be out of reach within his work. What he finally built was "only" a general-purpose Seraphis and Jamtis library that could be used to implement, among other things, a wallet. The good news however: That library turned out to be a marvel of solid software engineering and a very good base for our work.

In the first weeks we had so many devs showing interest in contributing work that I started to worry about coordination and finding enough reasonably independent parts of the wallet to work on concurrently. Alas, this never developed into a real problem: For the people without knowledge yet about the Monero codebase the challenge mostly proved to be too daunting, and the people with such knowledge had many additional Monero things on their hands at the same time and couldn't concentrate on the wallet alone.

Still, I can report some pretty good results:

u/j-berman wrote a *scanner*, a piece of software that reads through the blockchain starting at a specified height and finds all enotes / outputs that belong to a given Monero address - a core part of every wallet. He was using the Seraphis library to do so because that has full "read support" for pre-Seraphis transactions. The encouraging result: The scanner, although still at an early "version 1" so to say, is already a bit faster than the true-and-tried scanner inside the current component called *wallet2*.

u/dangerousfreedom1984 originally set out to write something like a frame for a wallet prototype. The bad news: That is still work in heavy progress. The good news: He wrote some nice so-called *proofs* on the way. For example, the basic code that allows to construct a proof that it was your wallet and not any other that made a particular Seraphis transaction exists already.

jeffro256 joined the workgroup a few months ago. He wrote a new component to read today's wallet files that is fully independent from code that will be retired after getting superseded by the Seraphis libary and the Seraphis wallet, which will be essential for a seamless migration. It's nice to have that settled already, but on the other hand this did not further the wallet proper yet.

So, how will things probably continue? I see again a mix of good news and bad news.

All 3 devs mentioned above know their way around the Seraphis library now and are able to productively write code that will be revelant for the switch to Seraphis and Jamtis. I think right now we have more dev capacity working on Seraphis related stuff than other, more general Monero stuff.

On the other hand there are surprising developments on the design front over the last few months. For quite some time it looked as if the designs of Seraphis and Jamtis were complete and set, and the "only" things left were implementing and getting them ready for the hardfork.

That has changed on two fronts at once.

jeffro256 started an initiative to fix a weakness of Jamtis that plays a role in connection with possible future third-party blockchain scanning services, somewhat similar to what MyMonero servers are doing today, but much more privacy-friendly. The already long and quite technical discussion starts [here](https://gist.github.com/tevador/50160d160d24cfc6c52ae02eb3d17024?permalink_comment_id=4665372#gistcomment-4665372). Personally, I would love to see that weakness gone, but it's also a bit disturbing that quite deep changes are on the table for something that looked rock-solid already, and if this gets accepted it means more delays of course.

u/kayabanerve started an even bigger "attack" on the current design of Seraphis: He set out to once and for all get rid of the weakest of Monero's privacy technologies, the rings, by using so called *full chain membership proofs*. Info about this story can be found [here](https://repo.getmonero.org/monero-project/ccs-proposals/-/merge_requests/403).

On the one hand it would be fantastic to see it implemented. On the other hand this alone may push the hardfork to Seraphis and Jamtis a full year further out, and as a more immediate consequence it will absorb a big chunk of u/j-berman 's capacity while he connects kayabanerve's code with the Seraphis library to test the feasibility of the technology.

Do we have to worry that Seraphis and Jamtis are still years away? If you ask me, Monero as of today stands pretty solid. For all we know, currently we don't have exploits, we don't have spam attacks, and the privacy holds up pretty well. This does not look like an emergency of any kind to me.

Still, of course we will try to move much faster in our second year than we did in our first. The signs that we will be able to look good.

If you are a dev and could imagine to become part of this adventure, read our "job offering" page [here](https://www.getmonero.org/2023/02/02/seraphis-jamtis-developer-opportunities.html).


