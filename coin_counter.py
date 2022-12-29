import main
import tkinter
import requests
import pandas as pd
from tkinter import *
import requests.exceptions
from pandastable import Table
from datetime import datetime



#global df_dict
df_dict={}

#global table_window
table_window=""

#global frame_grid
frame_grid = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1),(4,0),(4,1),(5,0),(5,1),(6,0),(6,1),(7,0),(7,1)]

#global counter
counter=0

#global table_list
table_list=[]

#global table_dict
table_dict={}

#global g_compare_dict
g_compare_dict={}


totals_dict={}


#Default accunts list for the log file
default_accounts=["KRAKEN","COINBASE","BITFINEX","TOTALS"]



""""Formating Functions"""

#Clears the scenario label
def clear():
    scenario_label.configure(text='')



#Resets all data structures, labels and entries  and closes account windows
def reset():
    global table_window
    global counter
    global table_list
    global df_dict
    global table_dict
    global g_compare_dict

    try:
        ctrl=table_window.winfo_exists()
        if ctrl==1:
            table_window.destroy()
        table_window=""

    except AttributeError: #if nothing was opened
        pass

    except tkinter.TclError: #if window was opened and then closed by user
        table_window=""


    counter=0
    table_list=[]
    df_dict={}
    table_dict={}
    g_compare_dict={}
    clear_all()




def clear_all():

    dif_table.model.df = table_df
    dif_table.redraw()
    first_entry.delete(0,END)
    second_entry.delete(0,END)
    min_entry.delete(0,END)
    current_account_label.configure(text="")
    clear_entries()




def clear_entries():
    # clear the entries
    wallet_name_entry.delete(0,END)
    coin_name_entry.delete(0, END)
    coin_amount_entry.delete(0, END)




"""" Getter/Setter functions """


#Gets the difference in amount between 2 excel sheets and displays them on the main window
def get_dif():




    # Format the date

    try:
        first_date=str(first_entry.get()) #older
        second_date=str(second_entry.get()) #latest
        min_amount=float(min_entry.get())



        compare_dict = {

            "Hesap": [],
            "Coin": [],
            first_date: [],
            second_date: [],
            "Coin Farkı": [],
            "Fiyat Farkı (USD)":[]
        }






        today_totals_df = pd.read_excel(f"{second_date}.xlsx", sheet_name="TOTALS")
        yesterday_totals_df = pd.read_excel(f"{first_date}.xlsx", sheet_name="TOTALS")

        #get the extra wallet sheets from the log files

        first_line = "" #older
        second_line = "" #latest

        files = open("logs.txt", "r")
        lines = files.readlines()#

        for entry in lines:
            if first_date in entry:
                first_line = entry.rstrip("\n").split(" ")[1:20]
            elif second_date in entry:
                second_line = entry.rstrip("\n").split(" ")[1:20]


        #declare lists to capture all added wallet dataframes from  the sheets
        yesterday_df_dict={}
        today_df_dict={}

        #get the dataframe from the sheets and append them to the lists
        for i in range(len(first_line)):
            #get the sheet name
            name=first_line[i]
            #get the dataframe
            df = pd.read_excel(f"{first_date}.xlsx", sheet_name=name)
            #append to list
            yesterday_df_dict.update({name:df})

        # get the dataframe from the sheets and append them to the lists
        for i in range(len(second_line)):
            # get the sheet name
            name = second_line[i]
            # get the dataframe
            df = pd.read_excel(f"{second_date}.xlsx", sheet_name=name)
            # append to list
            today_df_dict.update({name:df})


        yesterday_totals_dict = yesterday_totals_df.to_dict("list")
        today_totals_dict = today_totals_df.to_dict("list")

        for sheet in yesterday_df_dict:
            yesterday_df_dict[sheet]=yesterday_df_dict[sheet].to_dict("list")

        for sheet in today_df_dict:
            today_df_dict[sheet]=today_df_dict[sheet].to_dict("list")


        # Loop through the dictionaries and compare prices

        #Totals
        for y_entry in yesterday_totals_dict:
            for t_entry in today_totals_dict:

                if y_entry == t_entry:

                    y_token_value = yesterday_totals_dict[y_entry][0]
                    t_token_value = today_totals_dict[t_entry][0]
                    token_dif = round(t_token_value, 6) - round(y_token_value, 6)

                    if token_dif >=0.000009999 or token_dif<= -0.000009999:

                        t_usd_value = main.get_price(y_entry)


                        price_change = token_dif * float(t_usd_value)

                        if price_change >= min_amount or price_change <= -min_amount:
                            compare_dict["Hesap"].append("Totals")
                            compare_dict["Coin"].append(y_entry)
                            compare_dict[first_date].append(round(y_token_value, 6))
                            compare_dict[second_date].append(round(t_token_value, 6))
                            compare_dict["Fiyat Farkı (USD)"].append('{:.2f}'.format(price_change))
                            compare_dict["Coin Farkı"].append('{:.2f}'.format(token_dif))

                    break



        #Redraw the table with the new dataframe

        global g_compare_dict
        g_compare_dict=compare_dict
        compare_df = pd.DataFrame(compare_dict)
        dif_table.model.df=compare_df
        dif_table.redraw()

    except FileNotFoundError:

        scenario_label.configure(text=" Dosya bulunamdı. Lütfen mevcut dosya adı girin")
        root.after(7000,clear)

    except ValueError:

        scenario_label.configure(text=" Lütfen Min miktar girin ")
        root.after(7000, clear)




#Exports the differences to excel sheet
def get_dif_sheet():

    global  g_compare_dict

    df = pd.DataFrame(g_compare_dict)
    now_time = datetime.now()
    date_time = now_time.strftime("%m-%d-%Y, %H-%M-%S")

    with pd.ExcelWriter(f'Karşılaşma {date_time}.xlsx') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    scenario_label.configure(text='Export başarılı')

    #Reset tables and dictionaries
    clear_all()
    g_compare_dict = {}
    root.after(5000, clear)




#Exports all tables to an excel file
def get_excel():

    global totals_dict

    # get the date and time
    now_time = datetime.now()
    date_time = now_time.strftime("%m-%d-%Y,%H-%M-%S")

    ref_entry=date_time

    #Replace the totals dataframe with the new totals df including the wallet amounts

    #loop through the dict and find the extra wallets not in the default list
    for df in df_dict:
        if df not in default_accounts:
            #convert df to dict
            account_dict=df_dict[df].to_dict("list")

            coin_list=account_dict["Coin"]
            amount_list=account_dict["Amount"]

            wallet_dict={}
            index=0

            #create a temporary dict for the wallet
            while index < len(coin_list):
                wallet_dict.update({coin_list[index]: amount_list[index]})
                index += 1


            #loop through wallet dictionary and add entries to the totals dict

            white_list=[]

            for wallet_coin in wallet_dict:
                for total_coin in totals_dict:
                    if wallet_coin==total_coin:

                        totals_dict[total_coin][0] += float(wallet_dict[wallet_coin])
                        white_list.append(wallet_coin)


            #add any leftovers to the totals dict
            for coin in wallet_dict:
                if coin not in white_list:
                    totals_dict.update({coin:[wallet_dict[coin]]})


            #create a dataframe
            totals_df = pd.DataFrame(totals_dict)
            totals_df.insert(0, "TOTALS",[""])

            #Change the df dict
            df_dict["TOTALS"]=totals_df



    #append all the entries in the global df_dict to an excel sheet
    with pd.ExcelWriter(f'{date_time}.xlsx') as writer:
        for entry in df_dict:

            #get the dataframes
            df=df_dict[entry]

            #delete the table name column
            del df[entry]

            #append any added wallets to the log file entry for reference
            if entry not in default_accounts:

                ref_entry+=" "+entry

            #create the sheet
            df.to_excel(writer,sheet_name=entry,index=False)

    #save reference entry to log file
    with open("logs.txt", "a") as f:
        f.write(f"{ref_entry}\n")

    clear_all()
    reset()
    scenario_label.configure(text='Export başarılı')
    root.after(5000, clear)



#Get the coin amounts from kraken account and display them in an account window
def get_kraken():

    global table_window
    global counter
    global table_list
    global df_dict
    global table_dict
    global totals_dict
    global init_state_counter


    try:
        #get the dataframes for each sheet
        kraken_df = main.get_kraken()["df"]


    except requests.exceptions.ConnectionError:
        scenario_label.configure(text="Internet bağalması sorun var. Lütfen tekrar deneyin")
        root.after(5000,clear)
        return


    # append the global df_dict. Well use the keys as the names of the sheeets when we export to excel
    df_dict.update({"KRAKEN": kraken_df})


    #Insert title columns for the display table

    kraken_df.insert(0,"KRAKEN",[""])



    #Creat the table window
    table_window = Tk()
    table_window.title("ACCOUNTS")

    #create the local df_list to loop through for the griding
    df_list=[kraken_df]


    #Loop through the df_list and attach to the table window
    while counter<len(df_list):

        df=df_list[counter]


        frame = Frame(table_window)
        frame.grid(row=frame_grid[counter][0], column=frame_grid[counter][1])
        # create a table
        table = Table(frame, dataframe=df, height=80, width=750)
        table_list.append(table)
        table.show()

        counter +=1

    #Add the table to the tables dict in the same order as they are in the table list
    table_dict.update({"KRAKEN":table_list[0]})



    # open the log file and check the entries
    file = open("logs.txt", "r")
    # Get e list of entries from log file
    lines = file.readlines()
    # close the file
    file.close()

    # get the last entry from the log file
    latest_entry = ""

    for entry in lines:
        latest_entry = entry

    # divide it to see if there are additional wallets
    entry = latest_entry.rstrip("\n").split(" ")

    #Check if additioanl wallets exist
    if len(entry)>1:


            index=1

            file_name=entry[0]

            current_table=""

            while index <len(entry):

                #get the name of the sheet
                wallet_name=entry[index]

                #get the name of the current table for the windows display
                current_table=wallet_name

                #get the dataframe from the sheet
                wallet_df = pd.read_excel(f"{file_name}.xlsx", sheet_name=wallet_name)

                #get the dict from the dataframe
                wallet_dict=wallet_df.to_dict("list")

                #get the reference list for the heading column of the table
                empty_list=wallet_dict["Coin"]
                for i in range(len(empty_list)):
                    empty_list[i]=""

                #insert a column into the dataframe
                wallet_df.insert(0, wallet_name, empty_list)

                #append the dataframe to the global df_dict
                df_dict.update({wallet_name: wallet_df})

                #create a frame for the table
                frame = Frame(table_window)
                frame.grid(row=frame_grid[counter][0], column=frame_grid[counter][1])

                # create a table
                table = Table(frame, dataframe=wallet_df, height=80, width=750)

                #append table to to global table list
                table_list.append(table)

                #append table to the global table dict
                table_dict.update({wallet_name:table})

                table.show()

                counter+=1
                index+=1


            current_account_label.configure(text=f"Current table: {current_table}")
    root.after(1000, clear)



#Get the coin amounts from coinbase account and display them in an account window
def get_coinbase():

    global table_window
    global counter
    global table_list
    global df_dict
    global table_dict
    global totals_dict
    global init_state_counter


    try:
        #get the dataframes for each sheet
        coinbase_df = main.get_coinbase()["df"]


    except requests.exceptions.ConnectionError:
        scenario_label.configure(text="Internet bağalması sorun var. Lütfen tekrar deneyin")
        root.after(5000,clear)
        return


    # append the global df_dict. Well use the keys as the names of the sheeets when we export to excel
    df_dict.update({"COINBASE": coinbase_df})


    #Insert title columns for the display table

    coinbase_df.insert(0,"COINBASE",[""])



    #Creat the table window
    table_window = Tk()
    table_window.title("ACCOUNTS")

    #create the local df_list to loop through for the griding
    df_list=[coinbase_df]


    #Loop through the df_list and attach to the table window
    while counter<len(df_list):

        df=df_list[counter]


        frame = Frame(table_window)
        frame.grid(row=frame_grid[counter][0], column=frame_grid[counter][1])
        # create a table
        table = Table(frame, dataframe=df, height=80, width=750)
        table_list.append(table)
        table.show()

        counter +=1

    #Add the table to the tables dict in the same order as they are in the table list
    table_dict.update({"COINBASE":table_list[0]})



    # open the log file and check the entries
    file = open("logs.txt", "r")
    # Get e list of entries from log file
    lines = file.readlines()
    # close the file
    file.close()

    # get the last entry from the log file
    latest_entry = ""

    for entry in lines:
        latest_entry = entry

    # divide it to see if there are additional wallets
    entry = latest_entry.rstrip("\n").split(" ")

    #Check if additioanl wallets exist
    if len(entry)>1:


            index=1

            file_name=entry[0]

            current_table=""

            while index <len(entry):

                #get the name of the sheet
                wallet_name=entry[index]

                #get the name of the current table for the windows display
                current_table=wallet_name

                #get the dataframe from the sheet
                wallet_df = pd.read_excel(f"{file_name}.xlsx", sheet_name=wallet_name)

                #get the dict from the dataframe
                wallet_dict=wallet_df.to_dict("list")

                #get the reference list for the heading column of the table
                empty_list=wallet_dict["Coin"]
                for i in range(len(empty_list)):
                    empty_list[i]=""

                #insert a column into the dataframe
                wallet_df.insert(0, wallet_name, empty_list)

                #append the dataframe to the global df_dict
                df_dict.update({wallet_name: wallet_df})

                #create a frame for the table
                frame = Frame(table_window)
                frame.grid(row=frame_grid[counter][0], column=frame_grid[counter][1])

                # create a table
                table = Table(frame, dataframe=wallet_df, height=80, width=750)

                #append table to to global table list
                table_list.append(table)

                #append table to the global table dict
                table_dict.update({wallet_name:table})

                table.show()

                counter+=1
                index+=1


            current_account_label.configure(text=f"Current table: {current_table}")
    root.after(1000, clear)



#Get the coin amounts from bitfinex account and display them in an account window
def get_bitfinex():

    global table_window
    global counter
    global table_list
    global df_dict
    global table_dict
    global totals_dict
    global init_state_counter


    try:
        #get the dataframes for each sheet
        bitfinex_df = main.get_bitfinex()["df"]


    except requests.exceptions.ConnectionError:
        scenario_label.configure(text="Internet bağalması sorun var. Lütfen tekrar deneyin")
        root.after(5000,clear)
        return


    # append the global df_dict. Well use the keys as the names of the sheeets when we export to excel
    df_dict.update({"BITFINEX": bitfinex_df})


    #Insert title columns for the display table

    bitfinex_df.insert(0,"BITFINEX",[""])



    #Creat the table window
    table_window = Tk()
    table_window.title("ACCOUNTS")

    #create the local df_list to loop through for the griding
    df_list=[bitfinex_df]


    #Loop through the df_list and attach to the table window
    while counter<len(df_list):

        df=df_list[counter]


        frame = Frame(table_window)
        frame.grid(row=frame_grid[counter][0], column=frame_grid[counter][1])
        # create a table
        table = Table(frame, dataframe=df, height=80, width=750)
        table_list.append(table)
        table.show()

        counter +=1

    #Add the table to the tables dict in the same order as they are in the table list
    table_dict.update({"BITFINEX":table_list[0]})



    # open the log file and check the entries
    file = open("logs.txt", "r")
    # Get e list of entries from log file
    lines = file.readlines()
    # close the file
    file.close()

    # get the last entry from the log file
    latest_entry = ""

    for entry in lines:
        latest_entry = entry

    # divide it to see if there are additional wallets
    entry = latest_entry.rstrip("\n").split(" ")

    #Check if additioanl wallets exist
    if len(entry)>1:


            index=1

            file_name=entry[0]

            current_table=""

            while index <len(entry):

                #get the name of the sheet
                wallet_name=entry[index]

                #get the name of the current table for the windows display
                current_table=wallet_name

                #get the dataframe from the sheet
                wallet_df = pd.read_excel(f"{file_name}.xlsx", sheet_name=wallet_name)

                #get the dict from the dataframe
                wallet_dict=wallet_df.to_dict("list")

                #get the reference list for the heading column of the table
                empty_list=wallet_dict["Coin"]
                for i in range(len(empty_list)):
                    empty_list[i]=""

                #insert a column into the dataframe
                wallet_df.insert(0, wallet_name, empty_list)

                #append the dataframe to the global df_dict
                df_dict.update({wallet_name: wallet_df})

                #create a frame for the table
                frame = Frame(table_window)
                frame.grid(row=frame_grid[counter][0], column=frame_grid[counter][1])

                # create a table
                table = Table(frame, dataframe=wallet_df, height=80, width=750)

                #append table to to global table list
                table_list.append(table)

                #append table to the global table dict
                table_dict.update({wallet_name:table})

                table.show()

                counter+=1
                index+=1


            current_account_label.configure(text=f"Current table: {current_table}")
    root.after(1000, clear)




#Get the coin amounts form all accounts and displays them in an account window
def get_accounts():

    global table_window
    global counter
    global table_list
    global df_dict
    global table_dict
    global totals_dict
    global init_state_counter


    try:
        #get the dataframes for each sheet
        totals = main.get_total()
        totals_df= totals["totals_df"]
        kraken_df=totals["kraken_df"]
        coinbase_df=totals["coinbase_df"]
        bitfinex_df=totals["bitfinex_df"]
        totals_dict=totals["totals_dict"]



    except requests.exceptions.ConnectionError:
        scenario_label.configure(text="Internet bağalması sorun var. Lütfen tekrar deneyin")
        root.after(5000,clear)
        return



    # append the global df_dict. Well use the keys as the names of the sheeets when we export to excel
    df_dict.update({"KRAKEN": kraken_df})
    df_dict.update({"COINBASE": coinbase_df})
    df_dict.update({"BITFINEX": bitfinex_df})
    df_dict.update({"TOTALS": totals_df})


    #Insert title columns for the display table
    totals_df.insert(0, "TOTALS",[""])
    kraken_df.insert(0,"KRAKEN",[""])
    coinbase_df.insert(0,"COINBASE",[""])
    bitfinex_df.insert(0,"BITFINEX",[""])


    #Creat the table window
    table_window = Tk()
    table_window.title("ACCOUNTS")

    #create the local df_list to loop through for the griding
    df_list=[totals_df,kraken_df,coinbase_df,bitfinex_df]


    #Loop through the df_list and attach to the table window
    while counter<len(df_list):

        df=df_list[counter]


        frame = Frame(table_window)
        frame.grid(row=frame_grid[counter][0], column=frame_grid[counter][1])
        # create a table
        table = Table(frame, dataframe=df, height=80, width=750)
        table_list.append(table)
        table.show()

        counter +=1

    #Add the table to the tables dict in the same order as they are in the table list
    table_dict.update({"TOTALS":table_list[0]})
    table_dict.update({"KRAKEN":table_list[1]})
    table_dict.update({"COINBASE":table_list[2]})
    table_dict.update({"BITFINEX":table_list[3]})


    # open the log file and check the entries
    file = open("logs.txt", "r")
    # Get e list of entries from log file
    lines = file.readlines()
    # close the file
    file.close()

    # get the last entry from the log file
    latest_entry = ""

    for entry in lines:
        latest_entry = entry

    # divide it to see if there are additional wallets
    entry = latest_entry.rstrip("\n").split(" ")


    try:
        #Check if additioanl wallets exist
        if len(entry)>1:


                index=1

                file_name=entry[0]

                current_table=""

                while index <len(entry):

                    #get the name of the sheet
                    wallet_name=entry[index]

                    #get the name of the current table for the windows display
                    current_table=wallet_name

                    #get the dataframe from the sheet
                    wallet_df = pd.read_excel(f"{file_name}.xlsx", sheet_name=wallet_name)

                    #get the dict from the dataframe
                    wallet_dict=wallet_df.to_dict("list")

                    #get the reference list for the heading column of the table
                    empty_list=wallet_dict["Coin"]
                    for i in range(len(empty_list)):
                        empty_list[i]=""

                    #insert a column into the dataframe
                    wallet_df.insert(0, wallet_name, empty_list)

                    #append the dataframe to the global df_dict
                    df_dict.update({wallet_name: wallet_df})

                    #create a frame for the table
                    frame = Frame(table_window)
                    frame.grid(row=frame_grid[counter][0], column=frame_grid[counter][1])

                    # create a table
                    table = Table(frame, dataframe=wallet_df, height=80, width=750)

                    #append table to to global table list
                    table_list.append(table)

                    #append table to the global table dict
                    table_dict.update({wallet_name:table})

                    table.show()

                    counter+=1
                    index+=1

                current_account_label.configure(text=f"Current table: {current_table}")

    except ValueError: #incase a table is deleted in the excel file but it shows in the log file
        pass




    root.after(1000, clear)




#Create a table for a wallet and add it to the table windowwindow
def create_table():

    global counter
    global table_list
    global df_dict
    global table_dict



    #check if the tables window hasnt been launched yet
    if len(table_list) !=0:


        #Get wallet name
        wallet_name = wallet_name_entry.get()


        #create wallet dict using wallet name
        wallet_dict = {
            wallet_name:[""],
            "Coin": [""],
            "Amount": [""]
        }


        #create the dataframe from the wallet dict
        wallet_table_df = pd.DataFrame(wallet_dict)

        #append the wallet dataframe to the global dataframe dicitonary
        df_dict.update({wallet_name:wallet_table_df})

        #create frame and build the table
        frame=Frame(table_window)
        frame.grid(row=frame_grid[counter][0], column=frame_grid[counter][1])

        wallet_table = Table(frame, dataframe=wallet_table_df, height=80, width=750)

        #append the wallet table to the global table list
        table_list.append(wallet_table)

        #append the wallet table to the global table dict
        table_dict.update({wallet_name:wallet_table})

        #write the table to the frame
        wallet_table.show()

        #clear all entry fields
        clear_entries()
        counter += 1

        current_account_label.configure(text=f"Current Account: {wallet_name}")



    else:
        scenario_label.configure(text="Lütfen önce Get Account tuşuna basın")
        root.after(5000,clear)





#Add a coin to the current wallet table
def add_coin_entry():




    if table_window !="":
        #global counter
        global table_list
        global df_dict
        global table_dict

        #index to get the latest table that we added
        ref_counter= counter-1

        #get the table from the table list
        ref_table=table_list[ref_counter]

        #get the dataframe from that table
        ref_df=ref_table.model.df

        #get the original dictionary
        ref_dict=ref_df.to_dict("list")

        #get the wallet name
        wallet_name=""
        for name in ref_dict:
            wallet_name=name
            break



        #Get the coin name and amount
        coin_name=coin_name_entry.get()

        if coin_name == "" or coin_name==" ":
            scenario_label.configure(text="Lütfen coin adı girin")
            root.after(5000, clear)
            return

        try:
            coin_amount= float(coin_amount_entry.get())
        except ValueError:
            scenario_label.configure(text="Lütfen coin miktar girin")
            root.after(5000, clear)
            return


        if coin_name not in ref_dict["Coin"]:

            #Append the new coin name and amount
            if ref_dict["Coin"][0]=="":
                ref_dict["Coin"][0]=coin_name
                ref_dict["Amount"][0]=coin_amount


            else:
                ref_dict[wallet_name].append("")
                ref_dict["Coin"].append(coin_name)
                ref_dict["Amount"].append(coin_amount)


            #convert back to dataframe
            df=pd.DataFrame(ref_dict)

            #append the new df to the df_dict
            df_dict[wallet_name]=df




            #Redraw the table
            ref_table.model.df=df
            # append the new table to the table list
            table_list[ref_counter] = ref_table
            ref_table.redraw()

            #Clear the entries
            clear_entries()

        else:
            scenario_label.configure(text=f"{coin_name} tabloda zaten var. Lütfen Replace yada Remove tuşuna basın")
            root.after(5000,clear)





#Remove a coin from the current wallet table
def remove_coin_entry():

    if table_window != "":
        #global counter
        #global table_list
        global df_dict

        # index to get the latest table that we added
        ref_counter = counter - 1

        # get the table from the table list
        ref_table = table_list[ref_counter]

        # get the dataframe from that table
        ref_df = ref_table.model.df

        # get the original dictionary
        ref_dict = ref_df.to_dict("list")

        # get the wallet name
        wallet_name = ""
        for name in ref_dict:
            wallet_name = name
            break



        #reset the table
        if len(ref_dict[wallet_name])==1:
            ref_dict[wallet_name][0]=""
            ref_dict["Coin"][0]=""
            ref_dict["Amount"][0]=""

        # Remove the last entry
        if len(ref_dict[wallet_name])>1:
            ref_dict[wallet_name].pop()
            ref_dict["Coin"].pop()
            ref_dict["Amount"].pop()

        # convert back to dataframe
        df = pd.DataFrame(ref_dict)

        # append the new df to the df_dict
        df_dict[wallet_name] = df

        # Redraw the table
        ref_table.model.df = df
        ref_table.redraw()

        clear_entries()




#changes an exisitng asset balance in a table
def edit_table():

    global table_dict
    global df_dict

    if table_window !="":
        #grab the table name and coin info

        table_name=wallet_name_entry.get()
        coin_name=coin_name_entry.get()

        try:
            coin_balance=float(coin_amount_entry.get())
        except ValueError:
            scenario_label.configure(text="Lütfen coin miktar girin")
            root.after(5000, clear)
            return


        #check for the specific table
        try:
            table=table_dict[table_name]
            # get the dataframe
            wallet_df = table.model.df
        except KeyError:
            scenario_label.configure(text="Cüzdan adı bulunamadı. Lütfen mevcut cüzdan tablo adı girin")
            root.after(5000,clear)
            return




        #get the dicitonary
        wallet_dict=wallet_df.to_dict("list")

        #Get the index of the coin amount
        coin_list=wallet_dict["Coin"]

        if coin_name in coin_list:

        # Get the index of the coin amount

            index= coin_list.index(coin_name)


            #Edit the dictionary
            wallet_dict["Amount"][index]=coin_balance

            #Create new dataframe
            df=pd.DataFrame(wallet_dict)

            #Edit the global df_dict
            df_dict[table_name]=df


            #Append dataframe to table and redraw
            table.model.df=df

            table.redraw()

            clear_entries()

        else:
            scenario_label.configure(text=f"{coin_name} {table_name} tabloda bulunamadı. Lütfen mevcut coin girin")
            root.after(5000,clear)




#adds a new coin to an exisitng table
def add_edit_coin():

    global table_dict
    global df_dict

    if table_window !="":
        #grab the table name and coin info
        table_name=wallet_name_entry.get()
        coin_name=coin_name_entry.get()

        try:
            coin_balance=coin_amount_entry.get()
        except ValueError:
            scenario_label.configure(text="Lütfen coin miktar girin")
            root.after(5000, clear)
            return


        #check for the specific table
        table=table_dict[table_name]

        #get the dataframe
        wallet_df=table.model.df

        #get the dicitonary
        wallet_dict=wallet_df.to_dict("list")

        if coin_name not in wallet_dict["Coin"]:

            #add new entries
            if len(wallet_dict["Coin"])>1:
                wallet_dict[table_name].append("")
                wallet_dict["Coin"].append(coin_name)
                wallet_dict["Amount"].append(coin_balance)

            elif len(wallet_dict["Coin"])==1 and wallet_dict["Coin"][0] !="" :
                wallet_dict[table_name].append("")
                wallet_dict["Coin"].append(coin_name)
                wallet_dict["Amount"].append(coin_balance)

            else:
                wallet_dict[table_name][0]=""
                wallet_dict["Coin"][0]=coin_name
                wallet_dict["Amount"][0]=coin_balance



            #Create new dataframe
            df=pd.DataFrame(wallet_dict)

            #Edit the global df_dict
            df_dict[table_name]=df



            #Append dataframe to table and redraw
            table.model.df=df

            table.redraw()

            clear_entries()


        else:
            scenario_label.configure(text=f"{coin_name} tabloda zaten var. ")
            root.after(5000,clear)





#removes exisitng coin from an exisitng table
def remove_edit_coin():

    global table_dict
    global df_dict

    if table_window !="":
        # grab the table name and coin info
        table_name = wallet_name_entry.get()
        coin_name = coin_name_entry.get()


        # check for the specific table
        table = table_dict[table_name]

        # get the dataframe
        wallet_df = table.model.df

        # get the dicitonary
        wallet_dict = wallet_df.to_dict("list")

        # Get the index of the coin amount


        coin_list = wallet_dict["Coin"]


        try:
            index = coin_list.index(coin_name)
        except ValueError:
            scenario_label.configure(f"{coin_name} {table_name} tabloda bulunamadı")
            root.after(5000,clear)
            return


        # Remove dicitonary entries

        if len(coin_list)>1:
            del wallet_dict[table_name][index]
            del wallet_dict["Coin"][index]
            del wallet_dict["Amount"][index]

        else:
            wallet_dict[table_name][index]=""
            wallet_dict["Coin"][index]=""
            wallet_dict["Amount"][index]=""


        # Create new dataframe
        df = pd.DataFrame(wallet_dict)

        # Edit the global df_dict
        df_dict[table_name] = df

        # Append dataframe to table and redraw
        table.model.df = df

        table.redraw()

        clear_entries()







""""Control Functions"""

def excel_button_control():

    #for the account tables

    #tables have been created
    if table_window !="":
        scenario_label.configure(text='Hesaplanıyor. Lütfen bekleyin...')
        root.after(1000, get_excel)

    #For the comparison sheet //table is destroyed before
    elif table_window=="" and len(g_compare_dict) !=0:
        scenario_label.configure(text='Karşılaşma dosya indiriliyor. Lütfen bekleyin...')
        root.after(1000, get_dif_sheet)

    #tables havent been created
    elif table_window=="":
        scenario_label.configure(text="Lütfen önce Get Account tuşuna basın yada Karşılaştırma yapın")
        root.after(7000, clear)



def create_button_control():

    wallet_name=wallet_name_entry.get()



    wallet_name=wallet_name.split(" ")


    if wallet_name[0]!="" and  wallet_name[0] not in table_dict and len(wallet_name)==1:
        create_table()

    elif len(wallet_name) !=1:
        scenario_label.configure(text="Lütfen boşluk olmayan çüzdan adı girin")
        root.after(5000, clear)

    else:
        scenario_label.configure(text="Lütfen benzersiz bir cüzdan adı girin")
        root.after(5000,clear)



def add_button_control():

    wallet_name=wallet_name_entry.get()



    if wallet_name in table_dict:
        add_edit_coin()
    else:
        add_coin_entry()



def remove_button_control():

    wallet_name=wallet_name_entry.get()

    if wallet_name in table_dict:
        remove_edit_coin()
    else:
        remove_coin_entry()



def get_account_button_control():


    if len(table_dict)==0:

        choice=account.get()
        if choice =="totals":
            scenario_label.configure(text="Toplam hesaplanıyor. Lütfen bekleyin...")
            root.after(1000,get_accounts)
        elif choice=="kraken":
            scenario_label.configure(text="Kraken hesaplanıyor. Lütfen bekleyin...")
            root.after(1000, get_kraken)
        elif choice=="coinbase":
            scenario_label.configure(text="Coinbase hesaplanıyor. Lütfen bekleyin...")
            root.after(1000, get_coinbase)
        elif choice=="bitfinex":
            scenario_label.configure(text="Bitfinex hesaplanıyor. Lütfen bekleyin...")
            root.after(1000, get_bitfinex)
        else:
            scenario_label.configure(text="Lütfen hesabı seçin")
            root.after(5000, clear)

    else:
        scenario_label.configure(text="Lütfen önce Reset tuşuna basın")
        root.after(5000, clear)




""" Default table dataframe"""
table_df = pd.DataFrame({

    'Hesap': ["", "", "","","","","",""],
    "Coin":["", "", "","","","","",""],
    '1. Tarih (geçen)': ["          ", "", "","","","","",""],
    '2. Tarih (en son)': ["          ", "", "","","","","",""],
    'Coin Farkı': ["     ", "", "","","","","",""],
    'Fiyat Farkı (USD)': ["          ", "", "","","","","",""],

})



""" Main Window"""

#Create main table
root= Tk()
root.geometry('1000x700')
root.title('Coin Counter')



#Configure the rows and columns

root.resizable(True,True)
root.grid_columnconfigure(index=0,weight=1)
root.grid_columnconfigure(index=1,weight=1)
root.grid_columnconfigure(index=2,weight=1)
root.grid_columnconfigure(index=3,weight=1)


root.grid_rowconfigure(index=0,weight=1)
root.grid_rowconfigure(index=1,weight=1)
root.grid_rowconfigure(index=2,weight=1)
root.grid_rowconfigure(index=3,weight=1)
root.grid_rowconfigure(index=4,weight=1)
root.grid_rowconfigure(index=5,weight=1)



#Set the frames for the main window

title_frame= Frame(root)
check_button_frame=Frame(root)
table_frame=Frame(root)
option_frame=Frame(root)
entry_label_frame=Frame(option_frame)
entry_frame=Frame(option_frame)
wallet_label_frame=Frame(option_frame)
wallet_entry_frame=Frame(option_frame)
scenario_frame=Frame(root)
current_account_frame=Frame(check_button_frame)
button_frame=Frame(root)


#Grid the frames

title_frame.grid(row=0,column=0,sticky='nsew', )
check_button_frame.grid(row=1,column=0,sticky='nsew')
#Inside the check bıutton frame
current_account_frame.grid(row=0,column=4,sticky='nsew', pady=(10,10))
table_frame.grid(row=2,column=0,sticky="nsew",)
option_frame.grid(row=3,column=0,sticky="nsew",)
#Inside the option frame
entry_label_frame.grid(row=0,column=0,sticky="nsew",padx=(0, 200),pady=(10,10))
entry_frame.grid(row=1,column=0,sticky="nsew",)
wallet_label_frame.grid(row=0,column=1,sticky="nsew",padx=(0, 200),pady=(10,10))
wallet_entry_frame.grid(row=1,column=1,sticky="nsew")

scenario_frame.grid(row=4,column=0,sticky='nsew', pady=(10,10))
button_frame.grid(row=5,column=0,sticky='nsew', pady=(10,10))





#declare variable to get chosen account
account=StringVar()


#Check buttons
coinbase_check=Checkbutton(check_button_frame,variable=account, onvalue='coinbase', offvalue='', text='Coinbase', width=12,font=('Arial',13,'bold')).grid(row=0,column=0,padx=(0,0.5))
kraken_check=Checkbutton(check_button_frame,variable=account, onvalue='kraken', offvalue='', text='Kraken', width=12,font=('Arial',13,'bold')).grid(row=0,column=1,padx=(0,0.5))
bitfinex_check=Checkbutton(check_button_frame,variable=account, onvalue='bitfinex', offvalue='', text='Bitfinex', width=12,font=('Arial',13,'bold')).grid(row=0,column=2,padx=(0,0.5))
totals_check=Checkbutton(check_button_frame,variable=account, onvalue='totals', offvalue='', text='Totals', width=12,font=('Arial',13,'bold')).grid(row=0,column=3,padx=(0,0.5))

#Set the default table
dif_table = Table(table_frame, dataframe=table_df, height=100, width=350)
dif_table.grid(row=0,column=0)
dif_table.show()




#****Labels****
title= Label(title_frame, text='Hesaplar', font=('Arial',25,'italic'), fg='red', ).grid(row=0,column=0,sticky='w', pady=(40,0), padx=10)

entry_label= Label(entry_label_frame,text='Karşılaştırma',font=('Arial',18,'bold'), fg='red').grid(row=0, column=0,pady=5,padx=10, sticky='nsew')
wallet_label= Label(wallet_label_frame,text='Cüzdan Ekleme',font=('Arial',18,'bold'), fg='red').grid(row=0, column=0,pady=5,padx=10, sticky='nsew')

first_entry_label= Label(entry_frame,text='1. Dosya adı (geçen):',font=('Arial',10,'bold'), fg='red').grid(row=0, column=0,pady=5,padx=10, sticky='nsew')
second_entry_label= Label(entry_frame,text='2. Dosya adı (en son):',font=('Arial',10,'bold'), fg='red').grid(row=1, column=0,pady=5,padx=10, sticky='nsew')
min_entry_label= Label(entry_frame,text='Min fark miktar:',font=('Arial',10,'bold'), fg='red').grid(row=2, column=0,pady=5,padx=10, sticky='nsew')

wallet_name_label= Label(wallet_entry_frame,text='Cüzdan adı:',font=('Arial',10,'bold'), fg='red').grid(row=0, column=0,pady=5,padx=10, sticky='nsew')
coin_name_label= Label(wallet_entry_frame,text='Coin adı:',font=('Arial',10,'bold'), fg='red').grid(row=1, column=0,pady=5,padx=10, sticky='nsew')
coin_amount_label= Label(wallet_entry_frame,text='Coin miktarı:',font=('Arial',10,'bold'), fg='red').grid(row=2, column=0,pady=5,padx=10, sticky='nsew')

scenario_label= Label(scenario_frame, text='', font=('Arial',12,'bold'), fg='red' )
scenario_label.grid(row=0,column=0,sticky='w', pady=(0,0), padx=(20,0),)

current_account_label= Label(current_account_frame, text='', font=('Arial',12,'bold'), fg='red' )
current_account_label.grid(row=0,column=0,sticky='w', pady=(0,0), padx=(0,0),)





#****Entries****

first_entry= Entry(entry_frame,width=18)
second_entry= Entry(entry_frame,width=18)
min_entry=Entry(entry_frame,width=18)

wallet_name_entry=Entry(wallet_entry_frame,width=16)
coin_name_entry=Entry(wallet_entry_frame,width=16)
coin_amount_entry=Entry(wallet_entry_frame,width=16)


first_entry.grid(row=0,column=1,)
second_entry.grid(row=1,column=1,)
min_entry.grid(row=2,column=1,)


wallet_name_entry.grid(row=0, column=1)
coin_name_entry.grid(row=1, column=1)
coin_amount_entry.grid(row=2, column=1)



#****Buttons****


create_button=Button(wallet_entry_frame, text='Create', width=10 ,height=1, bg='yellow',font=('Arial',10,'bold'),command=create_button_control).grid(row=0,column=2, padx=(65,0),)
replace_button=Button(wallet_entry_frame, text='Replace', width=10 ,height=1, bg='#0f5edb',font=('Arial',10,'bold'),command=edit_table).grid(row=0,column=3, padx=(25,0),)

add_button=Button(wallet_entry_frame, text='Add', width=10 ,height=1, bg='green',font=('Arial',10,'bold'),command=add_button_control).grid(row=1,column=2, padx=(65,0),)
remove_button=Button(wallet_entry_frame, text='Remove', width=10 ,height=1, bg='red',font=('Arial',10,'bold'),command=remove_button_control).grid(row=1,column=3, padx=(25,0),)

get_account_button=Button(button_frame, text='Get Accounts', width=15 ,height=2, bg='#0f5edb', font=('Arial',10,'bold'),command=get_account_button_control).grid(row=6,column=0, padx=(100,40),)
excel_button=Button(button_frame, text='Export to Excel', width=15 ,height=2, bg='#287a07',font=('Arial',10,'bold'),command=excel_button_control).grid(row=6,column=1, padx=(40,50),)
compare_button=Button(button_frame, text='Compare', width=15 ,height=2, bg='yellow',font=('Arial',10,'bold'),command=get_dif).grid(row=6,column=3, padx=(40,50),)
reset_button=Button(button_frame, text='Reset', width=15 ,height=2, bg='red',font=('Arial',10,'bold'),command=reset).grid(row=6,column=4, padx=(40,50),)

root.mainloop()