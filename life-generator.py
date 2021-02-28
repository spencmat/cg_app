from tkinter import *
import csv
import tkinter as tk
import sys

#get the filename as an agr
filename = sys.argv[-1]

#create global variables
master_category = []
master_list = []
display_list = []
master_teammate = []

def write_categires_csv():
    f = open("output.csv", "w")
    f.write("categories\n")
    for i in master_category:
        f.write(i + "\n")


def file_out(out_type, out_num, out_category):
    f = open("output.csv", "w")
    f.write("input_item_type,input_item_category,input_number_to_generate,output_item_name,output_item_rating,output_item_num_reviews\n")

    for j in range(0, len(display_list)):
        f.write(out_type + "," + out_category + ",")
        f.write(out_num + "," + display_list[j][0] + ",")
        f.write(str(display_list[j][2]))
        f.write(" out of 5 stars,")
        f.write(str(display_list[j][1]))
        if len(master_teammate) > 0:
            for i in range(0, len(master_teammate)):
                if master_teammate[i][0] in display_list[j][0] or master_teammate[i][1] in display_list[j][0]:
                    f.write("," + master_teammate[i][2])
            f.write("\n")
        else:
            f.write(str(display_list[j][1]) + "\n")
    f.close()


#below is to open teammated file. If not present it will just open like normal.
try:
    with open('output_example.csv', 'r', encoding="utf-8") as csv_file:
        teammate_csv_data = csv.reader(csv_file)
        for read_line in teammate_csv_data:
            if read_line != ['input_keywords', 'output_content']:
                read_split = read_line[0].split(";")
                read_split.append(read_line[1])
                master_teammate.append(read_split)
except IOError:
    pass

#open the sample.csv which should always be present. No need to try/catch
with open('sample.csv', 'r', encoding="utf-8") as csv_file:
    csv_data = csv.reader(csv_file)
    for read_line in csv_data:
        temp_list = []
        temp_list.append(read_line[1])

        temp_list.append(read_line[5])

        temp = read_line[7]
        slice_object = slice(0,3,1)
        temp_list.append(temp[slice_object])

        category_list = []
        input_string = read_line[8]
        category_list = input_string.split(' > ')
        temp_list.append(category_list[0])

        temp_list.append(read_line[0])

        #produce the initial list to be displayed in the dropdown.
        if category_list[0] not in master_category and category_list[0] != "" and category_list[0] != "amazon_category_and_sub_category":
            master_category.append(category_list[0])
        master_list.append(temp_list)
    #Sort the initial list to be displayed in the dropdown.
    master_category.sort()


#main if statement. Will open UI in the event a CSV file was not inputed.
if len(sys.argv) <= 1:
    def submit():
        try:
            numToys_int = int(numToys.get())
            numToys_x_10 = 10 * numToys_int
            temp_list = []
            temp2_list = []

            for i in range(0, len(master_list)):
                if master_list[i][3] == option_1_val.get():
                    temp_list.append(master_list[i])

            temp_list.sort(key=lambda temp_list: temp_list[4])
            temp_list.reverse()
            temp_list.sort(key=lambda temp_list: int(temp_list[1]))
            temp_list.reverse()
            for i in range(0, numToys_x_10):
                temp2_list.append(temp_list[i])


            temp2_list.sort(key=lambda temp_list2: temp_list2[4])
            temp2_list.reverse()
            temp2_list.sort(key=lambda temp2_list: float(temp2_list[2]))
            temp2_list.reverse()

            for i in range(0, numToys_int):
                display_list.append(temp2_list[i])
            outputText.config(state="normal")
            outputText.delete(1.0, END)
            for i in range(0,len(display_list)):
                if len(master_teammate) == 0:
                    outputText.insert(tk.INSERT, display_list[i][0] + "\t " + display_list[i][1] + " \t" + display_list[i][2] + " \t" + display_list[i][3] + "\n\n")
                else:
                    outputText.insert(tk.INSERT, display_list[i][0] + "\t " + display_list[i][1] + " \t" + display_list[i][2] + " \t" + display_list[i][3] + "\n\n")
                    for j in range(0, len(master_teammate)):
                        if master_teammate[j][0] in display_list[i][0] or master_teammate[j][1] in display_list[i][0]:
                            outputText.insert(tk.INSERT, "--MORE INFO: " + master_teammate[j][2] + "\n\n")


            outputText.config(state="disabled")

            file_out("toys", numToys.get(), option_1_val.get())
        except ValueError:
            pass


    # make a Empty Tkinter window.
    mainWindow = Tk()
    mainWindow.geometry("900x600")

    # give the window a title name.
    mainWindow.title("Life Generator")

    # make the grid layout for the rows and columns.
    windowUI = Frame(mainWindow)

    #make everything left justified.
    windowUI.grid(column=0, row=0, sticky=W)

    #create the option drop down
    option_1_val = StringVar(mainWindow)                                            #create a string variable for the main screen
    option_1_val.set(master_category[0])                                            #settong default to prevent error
    choice_1 = master_category
    option_1 = OptionMenu(windowUI, option_1_val, *choice_1)
    Label(windowUI, text="Category Filter").grid(row=0, column=0, sticky=W)
    option_1.grid(row=1, column=0, sticky=W)

    #set widths for the optionwindows
    option_width = 20
    option_1.config(width = option_width)

    #add a integer entry for number of toys
    numToysVar = Label(mainWindow, text="Number of toys to output")
    numToys = Entry()
    numToysVar.grid(row=6, column=0, sticky=W)
    numToys.grid(row=7, column=0, sticky=W, padx=30, pady=10)

    #add output text area
    outputText=Text(mainWindow)
    outputText.config(state="disabled")
    outputText.grid(row=9, column=0, padx=30, pady=30)

    #add a button to run the selection
    submitBtn = Button(mainWindow, text="Submit", padx=50, command=submit)  #remember not to add the () after submit.
    submitBtn.grid(row=8, column=0)

    mainWindow.mainloop()

else:

    if filename == "--categories":
        write_categires_csv()
        exit()
    else:
        with open(filename, 'r', encoding="utf-8") as csv_file:
            csv_data = csv.reader(csv_file)
            for read_line in csv_data:
                #if heading just ignore:
                if read_line[0] == "input_item_type":
                    pass
                else:
                    numToys_int = int(read_line[2])
                    numToys_x_10 = 10 * numToys_int
                    temp_list = []
                    temp2_list = []
                    display_list = []
                    for row in range(0, len(master_list)):
                        if master_list[row][3] == read_line[1]:
                            temp_list.append(master_list[row])

                    temp_list.sort(key=lambda temp_list: temp_list[4])
                    temp_list.reverse()
                    temp_list.sort(key=lambda temp_list: int(temp_list[1]))
                    temp_list.reverse()
                    for i in range(0, numToys_x_10):
                        temp2_list.append(temp_list[i])

                    temp2_list.sort(key=lambda temp_list2: temp_list2[4])
                    temp2_list.reverse()
                    temp2_list.sort(key=lambda temp2_list: float(temp2_list[2]))
                    temp2_list.reverse()

                    for i in range(0, numToys_int):
                        display_list.append(temp2_list[i])

                    file_out(read_line[0], read_line[2], read_line[1])




