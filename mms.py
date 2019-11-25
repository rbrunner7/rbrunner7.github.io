import requests
import json
import time
import sys
import datetime
import keyboard

def main():

    port = "5555"
    if len(sys.argv) > 1:
        port = sys.argv[1]
        if port == "":
          port = "5555"
        elif port == "alice":
          port = "5555"
        elif port == "bob":
          port = "5556"
        elif port == "trent":
          port = "5557"
    print("Using RPC port " + port)

    # simple wallet is running on the localhost and port as given on command line
    url = "http://127.0.0.1:" + port +"/json_rpc"
    headers = {'content-type': 'application/json'}

    # Make an RPC call with the given method and any required parameters
    def execute_rpc_request2(method, params):
        rpc_input = { "method": method, "params": params }
        rpc_input.update({ "jsonrpc": "2.0", "id": "0" })
        response = requests.post(url, data=json.dumps(rpc_input), headers=headers)
        result = response.json()
        if "error" in result:
            print("**** An error occured: ****")
            print("Message: " + result["error"]["message"])
            print("Error code: " + str(result["error"]["code"]))
        return response

    # Print an RPC call response, e.g. for debugging purposes
    def print_response(response):
        print(response)
        print(json.dumps(response.json(), indent=4))

    # Get the list of all authorized signers, for translating signer indexes to cleartext info
    # Of course for production code no good idea to fetch signers again and again like here,
    # but we do here as sort of a stress-test, and for simplicity
    def get_all_signers():
        response = execute_rpc_request2("mms_get_all_signers", {})
        signers = response.json()["result"]["signers"]
        return signers
    
    # Print a single message
    def print_message(signers, message):
        sent = datetime.datetime.utcfromtimestamp(int(message["sent"]))
        print("{} {} {} {} {} {}"\
        .format(str(message["id"]).rjust(5), message["type"].ljust(20), message["direction"].ljust(4),\
        signers[message["signer_index"]]["label"].ljust(20), message["state"].ljust(15),\
        sent.strftime("%Y-%m-%d %H:%M:%S")))
    
    # List an array of messages if it contains any and print an info beforehand, inserting the number of messages
    def print_messages(info, messages):
        if len(messages) > 0:
            print(info.format(str(len(messages))))
            signers = get_all_signers()
            for message in messages:
                print_message(signers, message)
            print("")
    
    # List an array of messages, given by their ids, and print an info beforehand, inserting the number of messages
    def print_messages_by_id(info, message_ids):
        if len(message_ids) > 0:
            print(info.format(str(len(message_ids))))
            signers = get_all_signers()
            for message_id in message_ids:
                response = execute_rpc_request2("mms_get_message_by_id", {"id": message_id} )
                print_message(signers, response.json()["result"]["message"])
            print("")
    
    # Send all messages that are ready to send, e.g. after submitting wallet-created data generated new ones
    def send_all_ready_messages():
        response = execute_rpc_request2("mms_get_all_messages", {})
        result = response.json()["result"]
        if len(result) > 0:
            sent = []
            for message in result["messages"]:
                if message["state"] == "ready_to_send":
                    send_response = execute_rpc_request2("mms_send_message", { "id": message["id"] })
                    sent.append(message)
            print_messages("Sent the following {} messages:", sent)

    # Delete the message with the given id
    def delete_message(id):
        response = execute_rpc_request2("mms_delete_message", {"id": id} )
        
    # List the existing messages
    def list_messages():
        signers = get_all_signers()
        response = execute_rpc_request2("mms_get_all_messages", {})
        result = response.json()["result"]
        if len(result) > 0:
            print_messages("There are {} messages in the message store:", result["messages"])
        else:
            print("The message store does not contain any messages.")
        print("")

    # Delete all received messages that were sent longer than 2 minutes ago;
    # If you receive messages you may receive old messages that "hung" around in Bitmessage
    # together with new, fresh messages. This method here uses a possible (but not yet very good)
    # heuristic to keep the important new ones while getting the old ones out of the way.
    # This allows to start anew after some process was interrupted and resulted in a "mess"
    # with some messages sent, some not, some sent ones received, other ones not etc.
    # (If this takes place in the CLI wallet a human is of course very good to immediately
    # recognize any "old" messages and delete them. Here it's more difficult ...)
    def delete_old_messages():
        now = datetime.datetime.utcnow()
        response = execute_rpc_request2("mms_get_all_messages", {})
        result = response.json()["result"]
        if len(result) > 0:
            deleted = []
            for message in result["messages"]:
                if message["direction"] == "in":
                    sent = datetime.datetime.utcfromtimestamp(int(message["sent"]))
                    if (now - sent) > datetime.timedelta(0, 120):
                        delete_message(message["id"])
                        deleted.append(message)
            print_messages("Deleted {} messages as 'old':", deleted)

    # Get the content of the message with the given id
    def get_message_content(id):
        response = execute_rpc_request2("mms_get_message_by_id", {"id": id} )
        return response.json()["result"]["message"]["content"]
    
    # Check for any waiting messages, print them if any
    def check_for_messages():
        response = execute_rpc_request2("mms_check_for_messages", {})
        result = response.json()["result"]
        received = result["received"]
        if received:
            messages = result["messages"]
            print_messages("Received {} new messages:", messages)
    
    # Delete all messages, completely empty the message store
    def delete_all_messages():
        execute_rpc_request2("mms_delete_all_messages", {})
    
    # List the available choices of processings, as returned by "mms_get_processable_messages"
    def list_processing_choices(data_list):
        # Of course for production code no good idea to fetch signers again and again like here,
        # but we do here as sort of a stress-test, and for simplicity
        signers = get_all_signers()
        choice = 1    # Start with 1 because that's more "natural" for users
        for data in data_list:
            print(str(choice) + ": " + data["processing"] + " " + signers[data["receiving_signer_index"]]["label"])
            choice += 1
    
    # Get a processing to do by asking the user to choose if multiple, and otherwise simply giving back the only choice
    def get_processing_choice(data_list):
        num_choices = len(data_list)
        if num_choices == 1:
            return data_list[0]
        print("Enter choice (between 1 and " + str(num_choices) + "):")
        answer = raw_input()
        choice = int(answer) - 1
        return data_list[choice]
    
    # Set all messages contained in the processing data structure to "processed"
    def set_messages_to_processed(data):
        execute_rpc_request2("mms_set_messages_processed", { "data": data })
        if "message_ids" in data:
            print_messages_by_id("Set {} messages to 'processed':", data["message_ids"])

    # Show the wallet state, especially regarding multisig
    def print_wallet_state():
        response = execute_rpc_request2("mms_get_info", {} )
        info = response.json()["result"]
        print("Is MMS active?: " + str(info["active"]))
        print("Number of authorized signers: " + str(info["num_authorized_signers"]))
        print("Number of required signers: " + str(info["num_required_signers"]))
        print("Is signer configuration complete?: " + str(info["signer_config_complete"]))
        print("Are signer labels complete?: " + str(info["signer_labels_complete"]))
        
        response = execute_rpc_request2("mms_get_multisig_wallet_state", {} )
        state = response.json()["result"]["state"]
        print("Non-multisig address: " + state["address"])
        print("Net type: " + state["nettype"])
        print("Multisig?: " + str(state["multisig"]))
        print("Is multisig ready?: " + str(state["multisig_is_ready"]))
        print("Has partial key images?: " + str(state["has_multisig_partial_key_images"]))
        print("Multisig rounds passed: " + str(state["multisig_rounds_passed"]))
        print("Number of transfers: " + str(state["num_transfer_details"]))

        response = execute_rpc_request2("get_address", {} )
        info = response.json()["result"]
        print("Multisig main address: " + info["address"])

        response = execute_rpc_request2("get_balance", { "all_accounts": True, "strict": False } )
        info = response.json()["result"]
        print("Total wallet balance over all accounts: " + str(float(info["balance"])/1e12))
        print("Total currently unlocked balance: " + str(float(info["unlocked_balance"])/1e12))
        print("Blocks to unlock: " + str(info["blocks_to_unlock"]))
        print("")
    
    # Check whether we currently have suitable sync messages waiting from ALL other signers
    # Do so by checking whether we received waiting sync messages from all other signers that cover
    # all transfers as indicated by "num_transfer_details" in the wallet state;
    # Useful if we use "force_sync" and therefore cannot count on the wallet itself waiting until a complete
    # set of sync messages is present and tells us as it does with "normal" syncing;
    # An example how using RPC calls lets us implement more complex predicates and processings that the wallet
    # itself does not (or not yet) offer in the same way;
    # Implemented inefficiently like other methods here for the sake of simplicity and good testing of the
    # RPC methods
    def are_sync_messages_complete():
        response = execute_rpc_request2("mms_get_multisig_wallet_state", {} )
        state = response.json()["result"]["state"]
        current_height = state["num_transfer_details"]
        response = execute_rpc_request2("mms_get_info", {} )
        num_signers = response.json()["result"]["num_authorized_signers"]
        
        # Use an array of booleans to keep track of received messages; using such an array copes well with
        # the possibility that we have multiple messages from the same signer that all apply
        signer_is_ok = [False]*num_signers
        signer_is_ok[0] = True   # We don't need info from ourselves
        
        response = execute_rpc_request2("mms_get_all_messages", {})
        result = response.json()["result"]
        if len(result) > 0:
            for message in result["messages"]:
                if (message["state"] == "waiting") and (message["type"] == "multisig_sync_data")\
                and (message["wallet_height"] == current_height):
                    # This message satisfies all the conditions and thus really "counts": Note it
                    signer_is_ok[message["signer_index"]] = True
        
        print(signer_is_ok)
        for is_ok in signer_is_ok:
            if not is_ok:
                return False
        return True
    
    # Print the info about a single signer as returned e.g. by the "mms_get_signer" RPC call
    def print_signer(signer):
        print("Signer #" + str(signer["index"] + 1) + ":")
        print("Label: " + signer["label"])
        print("Transport (Bitmessage) address: " + signer["transport_address"])
        print("(Non-multisig) monero address: " + signer["monero_address"])
        print("Auto-config token: " + signer["auto_config_token"])
        print("Is auto-config currently running?: " + str(signer["auto_config_running"]))
        print("")
        
    # Print info about all signers
    def print_all_signers():
        response = execute_rpc_request2("mms_get_all_signers", {})
        result = response.json()["result"]
        for signer in result["signers"]:
            print_signer(signer)
    
    # Make sure the lables for all other signers are complete and thus everything ready for auto-config
    def assure_labels_complete():
        response = execute_rpc_request2("mms_get_info", {} )
        info = response.json()["result"]
        if info["signer_labels_complete"]:
            return
        for signer in range(2, info["num_authorized_signers"] + 1):
            print("Label for signer #" + str(signer) + ":")
            answer = raw_input()
            execute_rpc_request2("mms_set_signer", { "index": signer - 1, "set_label": True, "label": answer })
    
    # Init or re-init MMS
    def init_mms():
        response = execute_rpc_request2("mms_get_info", {} )
        info = response.json()["result"]
        if info["active"]:
            print("MMS is already active. Destroy signer config, delete all messages and re-init? yes/-")
            answer = raw_input()
            if answer != "yes":
                return
        print("Own label:")
        own_label = raw_input()
        print("Own transport (Bitmessage) address:")
        own_transport_address = raw_input()
        print("Number of authorized signers (the 'N' in 'M/N multisig'):")
        num_authorized_signers = int(raw_input())
        print("Number of required signers (the 'M' in 'M/N multisig'):")
        num_required_signers = int(raw_input())
        response = execute_rpc_request2("mms_init", {"own_label": own_label, "own_transport_address": own_transport_address,\
        "num_authorized_signers": num_authorized_signers, "num_required_signers": num_required_signers } )
        print_all_signers()

    def wait_and_process_any_messages(force_sync):
        while True:
            if keyboard.is_pressed("Ctrl"):
                break
            time.sleep(5)
            check_for_messages()

            if force_sync:
                # Get processible messages, and do so "aggressively" by trying to sync even if not strictly necessary
                response = execute_rpc_request2("mms_get_processable_messages", { "force_sync": True })
            else:
                response = execute_rpc_request2("mms_get_processable_messages", {})
            result = response.json()["result"]
            if not result["available"]:
                response = execute_rpc_request2("mms_get_processable_messages", {} )
                result = response.json()["result"]
            if result["available"]:
                data_list = result["data_list"]
                print("Newly possible processing(s):")
                list_processing_choices(result["data_list"])
                data = get_processing_choice(data_list)
                processing = data["processing"]
                contents = []
                if "message_ids" in data:
                    for id in data["message_ids"]:
                        contents.append(get_message_content(id))

                if processing == "make_multisig":
                    response = execute_rpc_request2("mms_get_info", {} )
                    num_required_signers = response.json()["result"]["num_required_signers"]
                    response = execute_rpc_request2("make_multisig", { "multisig_info": contents, "threshold": num_required_signers, "password": "" })
                    result = response.json()["result"]
                    if result["multisig_info"]:
                        print("Another key set exchange round is needed")
                        execute_rpc_request2("mms_process_wallet_created_data", { "type": "additional_key_set", "content": result["multisig_info"] })
                        send_all_ready_messages()
                    elif result["address"]:
                        print("Successfully went multisig, address is: " + result["address"])
                    set_messages_to_processed(data)
                      
                elif processing == "exchange_multisig_keys":
                    response = execute_rpc_request2("exchange_multisig_keys", { "multisig_info": contents, "password": "" })
                    result = response.json()["result"]
                    if result["multisig_info"]:
                        print("Another key set exchange round is needed")
                        execute_rpc_request2("mms_process_wallet_created_data", { "type": "additional_key_set", "content": result["multisig_info"] })
                        send_all_ready_messages()
                    elif result["address"]:
                        print("Successfully went multisig, address is: " + result["address"])
                    set_messages_to_processed(data)
                    
                elif processing == "create_sync_data":
                    response = execute_rpc_request2("export_multisig_info", {})
                    result = response.json()["result"]
                    response = execute_rpc_request2("mms_process_wallet_created_data", { "type": "multisig_sync_data", "content": result["info"] })
                    send_all_ready_messages()
                    set_messages_to_processed(data)
               
                elif processing == "process_sync_data":
                    if force_sync:
                        # We have to wait ourselves until we received a full set of suitable sync messages
                        do_sync = are_sync_messages_complete()
                    else:
                        do_sync = True
                    if do_sync:
                        response = execute_rpc_request2("import_multisig_info", { "info": contents })
                        set_messages_to_processed(data)
                        if force_sync:
                            break
                   
                elif processing == "process_auto_config_data":
                    for id in data["message_ids"]:
                        execute_rpc_request2("mms_process_auto_config_data_message", { "id": id })
                    response = execute_rpc_request2("mms_get_signer_config", {})
                    result = response.json()["result"]
                    signer_config = result["signer_config"]
                    response = execute_rpc_request2("mms_get_all_signers", {})
                    response_json = response.json()
                    result = response_json["result"]
                    for signer in result["signers"]:
                        if (not signer["me"]):
                            print(signer["label"])
                            execute_rpc_request2("mms_add_message", { "signer_index": signer["index"],\
                                "type": "signer_config", "direction": "out", "content": signer_config })                        
                    send_all_ready_messages()
                    set_messages_to_processed(data)

                elif processing == "process_signer_config":
                    response = execute_rpc_request2("mms_process_signer_config", { "signer_config": contents[0] })
                    set_messages_to_processed(data)
                
                elif processing == "send_tx":
                    execute_rpc_request2("mms_add_message", { "signer_index": data["receiving_signer_index"],\
                        "type": "partially_signed_tx", "direction": "out", "content": contents[0] })                        
                    send_all_ready_messages()
                    set_messages_to_processed(data)
                    
                elif processing == "sign_tx":
                    response = execute_rpc_request2("sign_multisig", { "tx_data_hex": contents[0] })
                    result = response.json()["result"]
                    message_type = "partially_signed_tx"
                    if len(result["tx_hash_list"]) > 0:
                        # Hashes available means it's fully signed now
                        message_type = "fully_signed_tx"
                    execute_rpc_request2("mms_add_message", { "signer_index": data["receiving_signer_index"],\
                        "type": message_type, "direction": "out", "content": result["tx_data_hex"] })                        
                    send_all_ready_messages()
                    set_messages_to_processed(data)

                elif processing == "submit_tx":
                    response = execute_rpc_request2("submit_multisig", { "tx_data_hex": contents[0] })
                    set_messages_to_processed(data)
                                         
                else:
                    print("Don't know (yet) how to do the following processing: " + processing)

    check_for_messages()
    list_messages()
    
    while True:
        print("Select processing:")
        print("0 = show wallet state")
        print("1 = list all messages")
        print("2 = delete all messages")
        print("3 = delete received but old messages")
        print("4 = prepare multisig")
        print("5 = wait and and auto-process any messages")
        print("6 = start auto-config")
        print("7 = enter auto-config token")
        print("8 = force a new sync round")
        print("9 = start transfer")
        print("10 = list all signers")
        print("11 = init or re-init MMS")
        print("99 = exit")
        answer = raw_input()
        if answer == "99":
            break

        elif answer == "10":
            print_all_signers()
        
        elif answer == "11":
            init_mms()

        elif answer == "0":
            print_wallet_state()

        elif answer == "1":
            list_messages()
            
        elif answer == "2":
            delete_all_messages()
        
        elif answer == "3":
            delete_old_messages()

        elif answer == "4":
            response = execute_rpc_request2("prepare_multisig", {})
            response_json = response.json()
            key_set = response_json["result"]["multisig_info"]
            print("Prepare multisig with key set: " + key_set)

            execute_rpc_request2("mms_process_wallet_created_data", { "type": "key_set", "content": key_set })
            send_all_ready_messages()
        
        elif answer == "5":
            print("Starting wait-and-process loop. Break with pressing and holding down Ctrl key")
            wait_and_process_any_messages(False)

        elif answer == "6":
            assure_labels_complete()
            execute_rpc_request2("mms_start_auto_config", {})
            response = execute_rpc_request2("mms_get_all_signers", {})
            response_json = response.json()
            result = response_json["result"]
            for signer in result["signers"]:
                token = signer["auto_config_token"]
                if (token):
                    print("Token for signer " + signer["label"] + ": " + token)
        
        elif answer == "7":
            print("Auto-config token: ")
            token = raw_input()
            execute_rpc_request2("mms_add_auto_config_data_message", { "auto_config_token": token })
            send_all_ready_messages()
        
        elif answer == "8":
            response = execute_rpc_request2("export_multisig_info", {})
            result = response.json()["result"]
            response = execute_rpc_request2("mms_process_wallet_created_data", { "type": "multisig_sync_data", "content": result["info"] })
            send_all_ready_messages()
            wait_and_process_any_messages(True)
                    
        elif answer == "9":
            print("Destination Monero address:")
            address = raw_input()
            print("Amount:")
            amount_str = raw_input()
            amount = long(float(amount_str)*1e12)
            destination = { "amount": amount, "address": address }
            response = execute_rpc_request2("transfer", { "destinations": [ destination ], "do_not_relay": True, "get_tx_hex": True })
            print_response(response)
            result = response.json()["result"]
            response = execute_rpc_request2("mms_process_wallet_created_data", { "type": "partially_signed_tx", "content": result["multisig_txset"] })

        else:
            print("Invalid processing")
              

if __name__ == "__main__":
    main()

