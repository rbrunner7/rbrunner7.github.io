# Beta-Testing the OpenBazaar Monero Integration

## Introduction

This document describes a first implementation of support for the Monero  / XMR cryptocurrency in the OpenBazaar server and desktop client, as a 5th or 6th coin in addition to BTC, BCH, LTC, ZEC and soon ETH. The software is an early beta, not fit for production, and not yet synchronized with the latest official versions of the OpenBazaar applications.

Devs or experienced and dedicated OpenBazaar users who want to beta-test Monero in OpenBazaar should find all the necessary information to do so in this document.

## TL;DR

If you are already experienced with both OpenBazaar and Monero here a high-level description how to get it running quickly:

* Get the beta server and client from rbrunner7's GitHub repository **Todo: Details**
* Create and fund a Monero Stagenet wallet or, more risky, a Mainnet wallet
* Set up and run a `monero-wallet-rpc` instance for that wallet
* Run the OpenBazaar server for a first time to let a migration run and add a new `XMR` wallet section to `config`, using `-t` startup option if using Stagenet
* Check the chapter *OpenBazaar Wallet Configuration Options* if you want extensive logging (recommended)
* Start server and client
* Success, hopefully: Use XMR. E.g. set up a test mode store with articles offering XMR as a supported payment coin, access from a second server/client pair to buy
* While testing consider: Only OpenBazaar direct payments with vendor online supported so far

## Monero Integration Architecture Overview

OpenBazaar offers seamless and dead-simple support for BTC and other similar cryptocurrencies because the OpenBazaar server includes already **everything** that is needed to work with them: It cares about access to the blockchains of those coins, it manages wallets on behalf of clients, automatically processes incoming transactions for all addresses under its control, etc.

All the code needed to do so is fully integrated.

With Monero it's quite different. The newly added Monero support code in the OpenBazaar server is **not** able to connect to any Monero blockchain; it's not even able to directly manage a wallet itself.

Why? The whole architecture of Monero is considerably more complex than that of Bitcoin and similar coins, and the code needed for blockchain access and to manage wallets therefore much bigger and more complicated. At the moment there simply exists no code that could be added to the OpenBazaar server as an integral part, and writing such code for this integration project would mean several months of work, which at least for now is clearly out of reach.

The solution: The Monero support in the OpenBazaar server interfaces with Monero's so-called *wallet RPC server*, a separate program that is part of the core Monero software.

This server needs to run alongside the OpenBazaar server whenever you want to use Monero in any way, and it in turn needs to connect to a Monero daemon for blockchain access. You can run your own Monero daemon as yet another separate program on your computer, or you can configure the RPC server to connect to a so-called *remote daemon* that some people of the Monero community kindly provide for the benefit of people that don't have a daemon of their own.

## Limitations: No Moderated and no Offline Payments

Out of the three possible forms of payments in OpenBazaar at the moment only the simplest one is supported for XMR: direct payments from buyer to vendor with the buyer online at the time of payment.

The use of moderation is **not** possible, and neither are payments with the vendor offline. (The desktop client isn't aware about this yet, tries nevertheless if you instruct it and will then fail with some possibly cryptic error message.)

These are admittedly serious limitations that make using Monero considerably less attractive, but like with the non-integration of wallet and blockchain access there are important reasons that simply left no choice for the time being:

Moderation works with multisig wallets and transactions which are, again, much more complex to build and handle in Monero than in Bitcoin and similar coins. Still, support might be added in the future, but would probably require a **joint** project of the OpenBazaar and Monero dev communities.

Things with unmoderated offline payments look more hopeful: Technically they also use multisig right now, but it looks like it's possible to change that for Monero, using part of the "infrastructure" that currently gets finalized for supporting Ethereum.

If interested you find some more technical background info about these limitions [in this document](https://rbrunner7.github.io/openbazaar.md).

## Mainnet, Stagenet, Testnet

Beside the usual *Mainnet* where your XMR have value Monero offers **two** public nets for testing with worthless "play coins": *Stagenet* and *Testnet*.

Stagenet usually runs software on the same release level as Mainnet and is thus a good place to be for testing this beta XMR integration: It works perfectly with the current Monero release Boron Butterfly of summer 2019 because it does not depend on any new features on the Monero side.

Testnet on the other hand is not sure to work with the latest public Monero release and is more geared towards devs for testing new Monero features with code they compile themselves.

Thus, for most readers, if you see anything "Test" in OpenBaazar, think Monero **Stage**net.

A good Stagenet blockchain explorer is [here](https://community.xmr.to/explorer/stagenet/); the same site also offers a [faucet](https://community.xmr.to/faucet/stagenet/) where you can get some free coins to work with.

If you do want to use Stagenet for your beta tests create a Stagenet wallet and connect to a Stagenet daemon. Otherwise, for added thrill, use a Mainnet wallet and connect to a daemon running on Mainnet.

If you start the OpenBazaar server with the `-t` command-line switch to use test mode it will allow connections to a Monero wallet RPC server either using a Stagenet or a Testnet wallet. If you start the OpenBazaar server normally it will only accept a RPC server using a Mainnet wallet.

The main address of the wallet is used to detect the type of net and allow or reject its use.

## Running the Monero Wallet RPC Server

As already mentioned for using Monero with the OpenBazaar integration described here you need to run the wallet RPC server, i.e. the `monero-wallet-rpc` executable, alongside the OpenBazaar server.

You use a **single** Monero wallet for one run of OpenBazaar; there is no need to switch between multiple wallets, and the current Monero integration isn't able to switch automatically anyway.

If you want to test with different wallets, e.g. a Stagenet wallet and a Testnet wallet, for switching you have to shut down both the OpenBazaar server and the wallet RPC server and restart the latter giving a different wallet file using the `--wallet-file` command-line parameter.

It's recommended to start the RPC server **first** and also wait until the wallet you use is fully synced before you start the OpenBazaar server. It should work the other way round, but with some error messages if you try to use XMR before everything is ready.

A typical full command line to start the wallet RPC server for Stagenet looks like this:

    ./monero-wallet-rpc --stagenet --wallet-file <wallet> --password <password> --rpc-bind-port 38083 --disable-rpc-login

With more detailed logging and using a remote node e.g. from XMRlab this becomes:

    ./monero-wallet-rpc --stagenet --wallet-file <wallet> --password <password> --rpc-bind-port 38083 --disable-rpc-login --log-level 1 --daemon-address testnet.node.xmrlab.com:38081

Details about the options used:

Securing the RPC server with a login, using a username and a password, is not yet supported; use the `--disable-rpc-login` command-line option, otherwise it will fail with HTTP error 401. (With your RPC server only serving *localhost* that's not terribly dangerous, but of course one argument more against using Mainnet already.)

Using a password for the wallet file itself is perfectly ok; use the `--password` command-line option for that.

Without any extra wallet configuration the OpenBazaar server uses port 38083 to connect when in test mode, so use `--rpc-bind-port 38083`.

Consider also using `--log-level 1` as explained in the chapter *Logging*.

For easy blockchain access using a remote node use `--daemon-address` as explained in chapter *Accessing the Monero Blockchain*.

## Accessing the Monero Blockchain

The Monero wallet RPC server `monero-wallet-rpc` needs access to the Monero blockchain to work. For this it has to connect to a *Monero daemon*.

The safest and thus recommended way is of course to run your own Monero daemon (the `monerod` executable in the Monero core software distribution) alongside OpenBazaar server and Monero wallet RPC server, as a third program, but to set that up you need to download somewhat over 70 GB of blockchain data, and you get one more server to "babysit" i.e. make sure it stays synced, start and stop it at the right time etc.

A usable compromise is to connect to a so-called *remote node*: There are people who operate publicly accessible Monero daemons for the benefit of wallet owners that can't or don't want to operate their own daemon.

One of the most prominent places to go for finding remote nodes is the [MoneroWorld website](https://moneroworld.com/).

For using a remote node specify the `--daemon-address` (with explicit port specification) or `--daemon-host` (using default ports) RPC server command-line parameter.

Addresses of Stagenet remote nodes for `--daemon-address`:

    testnet.node.xmrlab.com:38081
    node.xmr.to:38081

Addresses of Mainnet remote nodes:

    node.moneroworld.com:18089
    node.xmr.to:18081

## Logging

With beta software like this early Monero integration it's sometimes essential to see what happens, to diagnose configuration problems or notice early if something goes wrong because of some bug.

If you add `--log-level 1` as command-line option for the wallet RPC server you will see each RPC call as it happens, and you will also clearly see "blockchain events" like incoming transactions, both things which can be very useful.

The OpenBazaar daemon has a log file called `wallet.log` which in Linux resides either in `~/.openbazaar/logs` or `~/.openbazaar-testnet/logs`. Like the wallets for the other coins the Monero integration also writes wallet-related messages into this file.

But because the whole setup is more complicated, and because the Monero integration still may have bugs, there are more extensive possibilities for logging than for the other coins. You can configure it log to the mentioned `wallet.log` file in different levels of detail, and you can also configure it to log to the OpenBazaar console in parallel and also in different levels of detail.

Default is the same behaviour as the other wallets: Log to file, but only errors, and do not log to console. The chapter *OpenBazaar Wallet Configuration Options" tells you in detail how to change this. If in doubt use the following as value for the XMR `WalletOptions` key for quite extensive logging while beta-testing:

    { "LogToFile": true, "FileLogLevel": "INFO", "LogToConsole": true, "ConsoleLogLevel": "INFO" }

## OpenBazaar Wallet Configuration Options

The OpenBazaar daemon has a config file in JSON format. In Linux it's called `config` and is either in `~/.openbazaar` or `~/.openbazaar-testnet`.

With the Monero integration added to the OpenBazaar server it needs a `XMR` section / sub-object in the `Wallets` object in that file, whether you actually use Monero or not: The `Wallets` object always contains sub-objects for **all** supported currencies.

You don't usually add that `XMR` section yourself; it should get automatically added by a so-called *migration* if the OpenBazaar server notices at startup that it is still missing. 

There is a key `WalletOptions` with a default value of `null` but you can turn it into an object and add some key/value pairs according to your needs.

The keys in detail:

### RPCAddress

A string parameter that specifies the address of the Monero wallet RPC server, as an URL that includes a port number. Default is `"http://127.0.0.1:38083/json_rpc"` where port 38083 is usually taken when running the RPC server for Stagenet access.

In any case the port you give here must of course match the port that you use on the command line for `monero-wallet-rpc` - see the example parameter `--rpc-bind-port 38083` in chapter *Running the Monero Wallet RPC Server*.

When using Mainnet 18083 is often used, which results in a parameter value of 
`"http://127.0.0.1:18083/json_rpc"` for `RPCAddress`.

### LogToFile

A boolean parameter with the possible values of `true` and `false` (without any quotes) that switches logging to `wallet.log` on or off. Default value is `true`.

### FileLogLevel

A string parameter with possible values of `"ERROR"`, `"INFO"` and `"DEBUG"` (including quotes).

The meanings of these log levels in connection with the Monero integration:

* `"ERROR"`: Only log errors
* `"INFO"`: Log errors plus info i.e. messages that allow you to see step-by-step what wallets methods are called and what they return
* `"DEBUG"`: Log errors plus info plus "unimportant" info like the periodic checks for incoming transactions, or in other words log **everything** that can be logged

Default is `"ERROR"`: Only setting `LogToFile` to `true` and not setting `FileLogLevel` results in logging of errors only.

### LogToConsole

A boolean parameter with the possible values of `true` and `false` (without any quotes) that switches logging to the console on or off. Default value is `false`. The console here is the same "place" where the OpenBazaar server outputs its own messages to screen.

### ConsoleLogLevel

A string parameter with the same possible values of `"ERROR"`, `"INFO"` and `"DEBUG"` as the `FileLogLevel` parameter - details see there. Default is `"ERROR"` as well.

So, for maximum logging both to file and to console use the following as value for the whole `WalletOptions`:

    { "LogToFile": true, "FileLogLevel": "DEBUG", "LogToConsole": true, "ConsoleLogLevel": "DEBUG" }

(Of course add some value for `RPCAddress` if/as needed.)
