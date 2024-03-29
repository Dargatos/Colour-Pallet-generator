import tkinter as tk
import customtkinter as ctk
import os
import getpass
from tkinter import filedialog
from CTkColorPicker import *
from PIL import Image, ImageTk
from Pallet_generator import *
from ctk_color_picker import *
import sys
import winreg
# Yeah thas the code for UI not Pretty and way to less comments to understand that mess by questions if have dicord or via issues on github lol



class NavigatioFrame(ctk.CTkFrame):
	
	def __init__(
			self, 
			master, 
			home_button_event, 
			colours_button_event, 
			settings_button_event, 
			art_pallet_image,
			settings_image,
			home_image, 
			debug_command,
			appearance_main,
			command=None,
			**kwargs
			):
		super().__init__(master, **kwargs)
		self.grid_rowconfigure(5, weight=1)
		
		print("innit")
		
		self.appearance_main = appearance_main
		self.debug_command = debug_command
		self.home_button_event = home_button_event
		self.colours_button_event = colours_button_event
		self.settings_button_event = settings_button_event
		self.art_pallet_image = art_pallet_image
		self.settings_image = settings_image
		self.home_image = home_image

		self.fg_color = "Gray20"
		self.text_color_light = "White"
		self.text_color_dark = "Black"
		self.hover_color_dark = "Gray20"
		self.hover_color_light = "Gray70"

		self.navigation_frame_logo_label = ctk.CTkLabel(self,text=" Colour Generator", compound="left",font=ctk.CTkFont(size=15, weight="bold"))
		self.navigation_frame_logo_label.grid(row=0, column=0, padx=20, pady=20)   

		self.home_button = ctk.CTkButton(
			self, 
			corner_radius=0,
			height=40, 
			border_spacing=10, 
			text="Home",
			fg_color="transparent", 
			text_color=("White"),
			hover_color=("gray20"), 
			anchor="w",
			image=self.home_image,
			command=self.home_button_event
			)
		self.home_button.grid(row = 1, column = 0, sticky = "nsew")

		self.colours_button = ctk.CTkButton(
			self, 
			corner_radius=0,height=40, 
			border_spacing=10, text="Colours",
			fg_color="transparent", 
			text_color=("White"),
			hover_color=("gray20"), 
			anchor="w",
			image=self.art_pallet_image,
			command=self.colours_button_event
			)
		self.colours_button.grid(row = 2, column = 0, sticky = "nsew")

		self.settings_button = ctk.CTkButton(
			self, 
			corner_radius=0,
			height=40, 
			border_spacing=10, 
			text="Settings",
			fg_color="transparent", 
			text_color=("White"),
			hover_color=("gray20"), 
			anchor="w",
			image=self.settings_image,
			command=self.settings_button_event
			)
		self.settings_button.grid(row = 3, column = 0, sticky = "nsew")

		self.extra_button = ctk.CTkButton(self, 
			corner_radius=0,
			height=40, 
			border_spacing=10, 
			text="Extra(Test,Debug)",
			fg_color="transparent", 
			text_color=("White"),
			hover_color=("gray20"), 
			anchor="w",
			command=self.debug_command
			)
		self.extra_button.grid(row = 4, column = 0, sticky = "nsew")

		self.last_button_name = None
		self.last_button = None

		#self.theme_button = ctk.CTkOptionMenu(self,corner_radius=5,values=["Light","Dark","System"],command=self.change_appearance_mode_event)
		#self.theme_button.grid(row=6,column=0,padx=20,pady=10)

	def change_appearance_mode_event(self,new_appearance_mode: str):
		customtkinter.set_appearance_mode(new_appearance_mode)
		
		mode = str

		if new_appearance_mode == "System":
			result = self.is_windows_light_mode()
			mode = "Light" if result else "Dark"
		else: mode = new_appearance_mode

		if mode == "Light":
			self.extra_button.configure(text_color=self.text_color_dark,hover_color="Gray70")
			self.settings_button.configure(text_color=self.text_color_dark,hover_color="Gray70")
			self.colours_button.configure(text_color=self.text_color_dark,hover_color="Gray70")
			self.home_button.configure(text_color=self.text_color_dark,hover_color="Gray70")
			self.fg_color = "Gray70"
		if mode == "Dark":
			self.extra_button.configure(text_color="White",hover_color=self.hover_color_dark)
			self.settings_button.configure(text_color="White",hover_color=self.hover_color_dark)
			self.colours_button.configure(text_color="White",hover_color=self.hover_color_dark)
			self.home_button.configure(text_color="White",hover_color=self.hover_color_dark)
			self.fg_color = "Gray20"

		self.appearance_main(new_appearance_mode)
		self.highlite_buttons(self.last_button_name,"Gray20")
		
		
		
	def highlite_buttons(self, button_name, fg_color):
		
		fg_color = self.fg_color
		if self.last_button: 
			print("Wtf")
			self.last_button.configure(fg_color="transparent")
		
		button = getattr(self, f"{button_name}", None)
		print(button)

		if button: 
			print("Yes")
			button.configure(fg_color=fg_color)
		self.last_button_name = button_name
		self.last_button = button
	
	def is_windows_light_mode(self):
		try:
			key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
			value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
			return value == 1
		except Exception as e:
			print(f"Error: {e}")
			return None
	
class ColourFrameSettings(ctk.CTkFrame):
	def __init__(self,master,colour_frame_pallet, **kwargs):
		super().__init__(master, **kwargs)
		
		self.colour_frame_pallet = colour_frame_pallet
		self.send_len = False
		self.appearance = "Dark"

		self.gradient_var = tk.BooleanVar(value=False)
		self.checkbox_var = tk.StringVar()
		self.rowconfigure((0), weight=0)
		self.rowconfigure((1,2,3,4), weight=0)

		self.label_colour_settings = ctk.CTkLabel(self, corner_radius=50, text="Colour Settings", font=("_",20,"bold"), anchor="w")
		self.label_colour_settings.grid(row=0, column=0, sticky="swen", padx=10, pady=4)


		self.gradient_frame = ctk.CTkFrame(self,corner_radius=0,fg_color="Gray20")
		self.gradient_frame.grid(row=1, column=0,sticky="nsew", padx=15, pady=4)
		self.gradient_frame.grid_columnconfigure((0,1),weight=1)
		self.gradient_button = ctk.CTkCheckBox(self.gradient_frame, text="Gradient",border_color="White",variable=self.gradient_var,text_color="White",width=10,command=lambda: self.set_settings("gradient_button",self.gradient_var.get()))
		self.gradient_button.grid(row=0, column=0,sticky="nsew", padx=(0,0))
		self.gradient_value = ctk.CTkTextbox(self.gradient_frame,fg_color="Gray20",border_color="Gray20",width=30,font=("_",15),text_color="White",activate_scrollbars=False,wrap=None,height=5)
		self.gradient_value.insert("0.0",10)
		self.gradient_value.configure(state="disabled") # making state disabled in the beginning makes the placeholder text disappear
		self.gradient_value.grid(row=0, column=1, sticky="nswe",padx=(0,0))
		

		self.multiple_pallets_button = ctk.CTkCheckBox(self, text="Shuffel pallets",onvalue="On",border_color="White",offvalue="Off",text_color="White",command=self.button_clicked,variable=self.checkbox_var)
		self.multiple_pallets_button.grid(row=2, column=0, sticky="nswe", padx=15, pady=4)

	def button_clicked(self):
		current_value = self.checkbox_var.get()
		self.colour_frame_pallet.multiple_pallets_button(current_value)

	def set_settings(self,button,value):
		#print(value)
		self.colour_frame_pallet.set_settings(button,value)
		if button == "gradient_button":
			if value == True:
				self.gradient_value.configure(fg_color="Gray22",border_color="Gray22",state="normal")
				
				self.send_len = True
				self.repeat_send_len_event()
			else: 
				self.gradient_value.configure(fg_color="Gray20",border_color="Gray20",state="disabled")
				self.send_len = False
			
				
	def send_len_event(self):
		value = self.gradient_value.get("0.0","end")
		try:
			value = int(value)
			self.colour_frame_pallet.set_settings("gradient_len",value)
		except ValueError:""


	def repeat_send_len_event(self):
		self.send_len_event()
		# Schedule the repeat_send_len_event to be called again after 1000 milliseconds
		if self.send_len == False: return
		self.after(1000, self.repeat_send_len_event)

	def get_appearance(self,value):
		self.appearance = value
		
	def update_appearance(self):
		if self.appearance == "Light":
			self.gradient_button.configure(text_color="Black")

class HomeFrame(ctk.CTkFrame):
	def __init__(self,master,quit_event, **kwargs):
		super().__init__(master, **kwargs)

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)
		self.grid_rowconfigure((1,2,3), weight=0)

		self.quit_event = quit_event

		self.quit_button = ctk.CTkButton(self, corner_radius=5, border_spacing=10, text="I wanna leave", font=("_",20,),command=self.quit_event)
		self.quit_button.grid(row=3,column=0, sticky= "nsew", pady=4, padx=20)
			 
		self.textbox = ctk.CTkTextbox(self, width=250,)
		self.textbox.grid(row=0,column=0,padx=20, pady=(20,4), sticky="nswe")
		self.textbox.grid_propagate(True)

		self.button_2 = ctk.CTkButton(self,corner_radius=5, text = "Button2", font=("_",20))
		self.button_2.grid(row=2, column=0, sticky="nsew", pady=4, padx=20)

		self.button_1 = ctk.CTkButton(self,corner_radius=5, text = "Button1", font=("_",20),)
		self.button_1.grid(row=1, column=0, sticky="nsew", pady=4, padx=20)

		self.textbox.insert("0.0", "Some Help\n\n"+"on the left side bar the only funtional button is colours the rest is nonsense for now i think lol anyways when colours pressed a frame pops up where u have an empty pallet u can just add colours to it then press in the preview on Create folder shoul be set if not just click on it and select ur self enter name and Done.\n\n"+"in the poped up frame u have on the right settings also not done tho one actually work even if he isnt helping u anyways lol")


class SettingsFrame(ctk.CTkFrame):
	def __init__(self,master, **kwargs):
		super().__init__(master, **kwargs)

		self.grid_rowconfigure((0,1),weight=0)

		self.setting_frame_bt1 = ctk.CTkButton(self,text="bt1")
		self.setting_frame_bt1.grid(row=0, column=0)
		self.setting_frame_bt2 = ctk.CTkButton(self,text="bt2")
		self.setting_frame_bt2.grid(row=1, column=0)


class ColourFramePallet(ctk.CTkFrame):
	def __init__(self,master,right_arrow_image,left_arrow_image,update_preview_image,gradient_length, **kwargs):
		super().__init__(master, **kwargs)

		self.grid_rowconfigure((0,2),weight=0)
		self.grid_rowconfigure((1),weight=1)		
		self.grid_columnconfigure((0,1,2),weight=0)

		self.update_preview_image = update_preview_image
		self.right_arrow_image = right_arrow_image
		self.left_arrow_image = left_arrow_image
		self.gradient_length = gradient_length


		self.colour_pallets_frames = []
		self.colour_parent_array =[]
		self.colour_array = []

		self.latest_new_frame= None
		self.button_id = None
		self.last_fg_color = None
		self.current_frame = None
		self.old_len = 10

		self.gradient_button = False
		self.shuffel = False



		self.gradient_len = 10
		self.label_colour_pallet = ctk.CTkLabel(self, corner_radius=0, text=f'{"Color Pallet"} {self.current_frame}',font=("_",20,"bold"),fg_color="transparent",width=10)
		self.label_colour_pallet.grid(row=0, column=0, columnspan=3, sticky="nswe", padx=20, pady=(10,0))


		self.next_pallet_button= ctk.CTkButton(self, corner_radius=6,fg_color="Gray20",text="",height=20,width=20, hover_color="Gray25",image=right_arrow_image,command=lambda: self._frame(None,None,+1))
		#self.next_pallet_button.grid(row=0,column=2,sticky="",pady=(10,0),padx=(10,0))
		
		self.previous_pallet_button= ctk.CTkButton(self, corner_radius=6,fg_color="Gray20",text="",height=20,width=20, hover_color="Gray25",image=left_arrow_image,command=lambda: self._frame(None,None,-1))
		#self.previous_pallet_button.grid(row=0,column=0,sticky="",pady=(10,0),padx=(0,10))

		self.button_colour_add = ctk.CTkButton(
			self,
			corner_radius=6,
			text="Add",
			font=("_",15),
			width=10,
			height=35,
			hover_color="Gray23",
			fg_color="transparent",
			command=self.AskColor
			)
		self.button_colour_add.grid(row=2,column=0,padx=(15,5),pady=(0,10))

		self.button_colour_remove = ctk.CTkButton(
			self,
			corner_radius=6,
			text="Remove",
			font=("_",15),
			width=10,
			height=35,
			hover_color="Gray23",
			fg_color="transparent",
			command=lambda:self.colour_choosen(self.button_id,"delete"),
			)
		self.button_colour_remove.grid(row=2,column=1,padx=(5,5),pady=(0,10))

		self.button_colour_edit = ctk.CTkButton(
			self,
			corner_radius=6,
			text="Edit",
			font=("_",15),
			width=10,
			height=35,
			hover_color="Gray23",
			fg_color="transparent",
			command=lambda:self.colour_choosen(self.button_id,"edit")
			)
		self.button_colour_edit.grid(row=2,column=2,padx=(5,15),pady=(0,10))
		

		self.colour_list_parent = ctk.CTkFrame(self, corner_radius=6,fg_color="Gray20")
		self.colour_list_parent.grid(row=1, column=0,columnspan=3, padx=10, pady=10, sticky="nswe")
		self.colour_list_parent.grid_columnconfigure(0,weight=1,minsize=222)
		self.colour_list_parent.grid_rowconfigure(0,weight=1)

		self.add_colour_frame()
		self.bind("<Configure>", self.hide_scrollbar)

	def set_settings(self,button,value):
		setattr(self, f"{button}", value)
		if button == "gradient_len": self.observe_gradient_len()

	def observe_gradient_len(self):
		new_len = self.gradient_len
		if new_len != self.old_len:
			self.update()
		self.old_len = new_len
		
	def printarray(self):
		colors = self.current_colour_array()
		place = self.current_frame_place()
		temp_array = []
		for button in colors:
			color = button.cget("fg_color")
			temp_array.append(color)
		print(f'{"Array"}{place + 1}{temp_array}')
		

	def multiple_pallets_button(self,value):
		
		if value == "On":
			self.next_pallet_button.grid(row=0,column=2,sticky="",pady=(10,0),padx=(10,0))
			self.previous_pallet_button.grid(row=0,column=0,sticky="",pady=(10,0),padx=(0,10))
			self.shuffel = True
		else:
			self.next_pallet_button.grid_forget()
			self.previous_pallet_button.grid_forget()
			self.shuffel = False
			
	def update(self):
		colors = self.current_colour_array()
		temp_array = []
		for button in colors:
			color = button.cget("fg_color")
			temp_array.append(color)
		color_gen = ColorGenerator()	

		if self.shuffel:
			print("Shuuffffel")
			colour_parent_ar = []

			for sub_array in self.colour_parent_array: # WTF IM doint that rn soo ugly make functions for that shit like wtf, Espacially importn an fnt for the converting into an hex ar
				if sub_array == []: continue # Runs into erro if ya delete all colour in pallet so just continue if there arent any lol
				print(f"parent len{len(self.colour_parent_array)}")
				print(self.colour_parent_array)
				colour_ar = []
				for i, element  in enumerate(sub_array):
					print(element)
					colour = element.cget("fg_color")
					colour_ar.append(colour)


				if self.gradient_button:
						lenght = self.gradient_len if self.gradient_len > 5 else 5
						colour_ar = ColorGenerator.generate_gradient_colors(self,colour_ar,lenght)


			


				colour_parent_ar.append(colour_ar)

			temp_array = ColorGenerator.shuffel(self,colour_parent_ar)


		elif self.gradient_button == True:

			lenght = self.gradient_len if self.gradient_len > 5 else 5 # Checks length cause 1 makes Error

			temp_array = ColorGenerator.generate_gradient_colors(self,temp_array,lenght)

		

		image = color_gen.create_color_image(temp_array)
		self.update_preview_image(image)

	def save_pallet(self,place,name):

		colors = self.current_colour_array()

		temp_array = []
		for item in colors:
			color = item.cget("fg_color")
			temp_array.append(color)

		if self.shuffel:
			temp_array = ColorGenerator.shuffel(self,self.colour_parent_array)

		if self.gradient_button == True:
			lenght = self.gradient_len
			temp_array = ColorGenerator.generate_gradient_colors(self,temp_array,lenght)

		
		ColorGenerator.save_colors_to_file(self,temp_array,name,place)


	
	def current_frame_place(self):
		place = self.colour_pallets_frames.index(self.current_frame)
		return place

	def current_frame_event(self):
		frame_place = self.current_frame_place()

		frame = self.colour_pallets_frames[frame_place]
		self.current_frame = frame
		return frame

	def current_colour_array(self):

		pos = self.current_frame_place()

		if self.colour_parent_array:
			array = self.colour_parent_array[pos]
			return array
		
		self.colour_parent_array.append(self.colour_array)
		array = self.colour_parent_array[pos]
		return array
		
	def _colour(self,command):
		if command == "add":self.add_color
		if command == "edit":self.edit_colour
		if command == "remove":self.remove_colour

	def _frame(self,frame=None,command = None,where = None):

		current_array = self.current_colour_array()

		if frame == None:
			frame = self.current_frame_event()

		if where == None: # when colours i called with where == None no frame will be placed or created
			return
		
		if len(self.colour_pallets_frames) == self.current_frame_place() +1 and where == 1: # if frame is on last place of array and u wanna create a new one
			
			if(len(current_array) == 0): # if current frame has no colour no need for continueing
				return
			
			self.add_colour_frame()
			return

		if self.current_frame_place == 0 and where == -1:# if u are on last frame in array and wanna go back no frame will be placed
			return
		
		next_frame = self.colour_pallets_frames[self.current_frame_place()+ where]
		self.place_frame(next_frame)

		if(len(current_array) == 0):#if u wanna go back to an existing frame and current is empty

			self.latest_new_frame.destroy()
			array = self.colour_pallets_frames[:-1]
			self.colour_pallets_frames = array

			parent_ar = self.colour_parent_array[:-1]
			self.colour_parent_array = parent_ar

		self.update()
		

	def add_colour_frame(self):
		colour_array = []
		# Creates new Frame
		frame = ctk.CTkScrollableFrame(self.colour_list_parent, corner_radius=0, scrollbar_button_color="Gray17")
		frame.grid_columnconfigure(0,weight=1)
		self.current_frame = frame
		self.colour_parent_array.append(colour_array)
		self.colour_pallets_frames.append(frame)
		self.place_frame(frame)
		self.latest_new_frame = frame
		#self.update()


	def place_frame(self, frame):
		frame.grid(row=0, column=0,sticky="nswe")
		self.current_frame = frame
		frame_place = self.current_frame_place()
		self.label_colour_pallet.configure(text=f'{"Colour Pallet"} {frame_place + 1}')
		for i ,item in enumerate(self.colour_pallets_frames):		
			if item != frame:
				item.grid_forget()
	

	def AskColor(self):
		AskColor(command=self.add_color)
		 # open the color picker


	def add_color(self,color):
		current_frame = self.current_frame
		place = self.current_frame_place()
		colour_array = self.colour_parent_array[place]

		darker_color = self.darken_color(color)#calls function to make a darker version of color
	
		# Creates button and places it
		button = ctk.CTkButton(current_frame, text=f"{color}", font=("_",15,"bold"), text_color="Black", corner_radius=6,fg_color=color,hover_color=darker_color)
		button.grid(row=len(colour_array), column=0, pady=5,sticky="nswe")
		button.configure(command=lambda btn=button: self.colour_choosen(btn,"change"))

		# save button in array
		
		colour_array.append(button)
		self.update()
		self.after(10, lambda: self.hide_scrollbar("<Configure>"))

	def colour_choosen(self, button_id, action):
		self.change = action

		if action == "change": 
			

			if self.button_id is not None: 
				self.button_id.configure(fg_color=self.last_fg_color, font=("_", 15, "bold"))

			self.button_id = button_id
			hover_color = button_id.cget("hover_color")
			self.last_fg_color = button_id.cget("fg_color")
			button_id.configure(fg_color=hover_color, font=("_", 15, "bold", "underline"))

		if action == "delete":self.delete_color(self.button_id)
		if action == "edit":self.edit_button(self.button_id)
		
	def delete_color(self, item):
        # Find the index of the button in the list
		colour_list = self.current_colour_array()
		last = colour_list[-1]
		

		# if Button was Pressed delet last pressed button
		if item != None: 
			item.destroy()

			colour_list.remove(item)
			self.button_id = None
		
		# if Button wasnt pressed delete last button in list
		else:

			last.destroy()
			colour_list.remove(last)

		self.hide_scrollbar("<Configure>")
		self.update()
			
	def edit_button(self, button):
		
		if button:
			pick_color = AskColor() # open the color picker
			color = pick_color.get() # get the color string
			darker_color = self.darken_color(color)
			button.configure(fg_color=color,hover_color=darker_color)
			self.last_fg_color = color
			self.update()


	def darken_color(self, hex_color, factor=0.7):
    	# Convert hex color to RGB

		rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

		# Darken the color by multiplying each component by the factor
		darkened_rgb = tuple(int(c * factor) for c in rgb_color)

    	# Ensure values are in the valid range (0-255)
		darkened_rgb = tuple(max(0, min(255, c)) for c in darkened_rgb)

    	# Convert the darkened RGB back to hex
		darkened_hex = "#{:02x}{:02x}{:02x}".format(*darkened_rgb)

		return darkened_hex

	def hide_scrollbar(self,event):

		#print(self.current_frame.winfo_height())
	
		if self.current_frame.winfo_height() >= self.colour_list_parent.winfo_height()-20:
			self.current_frame.configure(corner_radius=6, scrollbar_button_color="Gray")

		else: 
			self.current_frame.configure(corner_radius=6, scrollbar_button_color="Gray17")


class ColourFramePreview(ctk.CTkFrame):
	def __init__(self,master,create_pallet_event,folder_path, **kwargs):
		super().__init__(master, **kwargs)

		

		self.preview_image = None
		self.folder_path = folder_path
		self.create_pallet_event = create_pallet_event
		self.grid_columnconfigure((0,2), minsize=50)
		self.grid_columnconfigure((1),weight=1, minsize=51)
		self.grid_rowconfigure((0,2),weight=0)
		self.grid_rowconfigure((1),weight=1)

		self.overview_label = ctk.CTkLabel(self, corner_radius=0, text="Overview", font=("_",30,"bold"),anchor="center", fg_color="transparent")
		self.overview_label.grid(column=0,columnspan=(3), row=0, sticky="new", padx=20, pady=20)

		self.reload_button = ctk.CTkButton(self, text="", width= 20, height=20,fg_color="transparent",hover_color="White",hover=True)
		self.reload_button.grid(column=2, row=0, sticky="n", padx=20, pady=20)
		
	 
		self.preview_image_label = ctk.CTkLabel(self, corner_radius=10, text="", image=None, fg_color="transparent")
		self.preview_image_label.grid(row=1, columnspan=(3), sticky="nsew", padx=10, pady=0)

		self.create_color_button = ctk.CTkButton(self, corner_radius=6, text="Create",fg_color="Gray17",hover_color="Gray25",font=("_",30,"bold","italic"),command=self.create)
		self.create_color_button.grid(row=2,columnspan=3,padx=10,pady=(0,20))

		
		self.preview_image_label.bind("<Configure>", self.resize)


	def create(self):
		self.create_final_pallet = CreateFinalPallet(master=self,create_pallet_event = self.create_pallet_event,directory = self.folder_path)
		self.create_final_pallet.lift()

	def update(self,image):
		self.preview_image = image
		self.resize()
		

	def resize(self, event=None):

		if self.preview_image is None:
			return
		
		if event:
			new_width = event.width 
			new_height = event.height
		else:
			new_height = self.preview_image_label.winfo_height()
			new_width = self.preview_image_label.winfo_width()	
		min_size  = min(new_width, new_height) * 0.9
		size = (int(min_size), int(min_size)) 

		resized = self.preview_image.resize((size))

		blank_image = Image.new("RGBA", (self.preview_image_label.winfo_width(), self.preview_image_label.winfo_height()), (0, 0, 0, 0))

		x_position = (self.preview_image_label.winfo_width() - int(min_size)) // 2
		y_position = (self.preview_image_label.winfo_height() - int(min_size)) // 2
		blank_image.paste(resized, (x_position, y_position))
		self.resized_preview_image = ImageTk.PhotoImage(blank_image)

		self.preview_image_label.configure(image=self.resized_preview_image)
		self.preview_image_label.grid(row=1, columnspan=3, sticky="nsew", padx=10, pady=10)

		"""self.rezied_preview_image =  ImageTk.PhotoImage(resized)
		self.preview_image_label.configure(image=self.rezied_preview_image)
		self.preview_image_label.grid(row=1,columnspan=(3), sticky="nsew", padx=10, pady=10)"""


class CreateFinalPallet(ctk.CTkToplevel):
	def __init__(self,
				 master,
				 create_pallet_event,
				 directory: str = "Set Directory", 
				 **kwargs):
		super().__init__(master,**kwargs)


		image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Files")
		self.folder = ctk.CTkImage(light_image=Image.open(os.path.join(image_path,"folder-dark.png")),dark_image=Image.open(os.path.join(image_path,"folder-light.png")))

		self.title("Create Pallet")
		self.geometry("550x200+600+300")
		self.resizable(width=False,height=False)
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)


		screen_width = self.winfo_screenwidth()
		screen_height = self.winfo_screenheight()

		x_coordinate = (screen_width) // 2
		y_coordinate = (screen_height) // 2

		self.main_frame = ctk.CTkFrame(self,fg_color="transparent")
		self.main_frame.grid(row=0,column=0,sticky="nswe")
		#self.main_frame.grid_rowconfigure((),weight=0)
		self.main_frame.grid_rowconfigure((0,1,2),weight=0)
		self.main_frame.grid_columnconfigure(1,weight=0)

		self.create_pallet_event = create_pallet_event

		if directory == None: self.directory = "Set Directory"
		else:self.directory = directory


		self.label = ctk.CTkLabel(self.main_frame,text="Create Colorset",font=("",25,"bold","underline"))
		self.label.grid(row=0,column=1,padx=50,pady=(10,5),sticky="nsew")

		self.change_directory = ctk.CTkButton(self.main_frame, text=self.directory, font=("_",13,"roman"),fg_color="Gray15",border_color="Gray70",border_width=2,height=40,command=self.set_directory_event,hover_color="Gray24",image=self.folder,anchor="w",compound="left",width=450)
		self.change_directory.grid(row=1,column=1,padx=50,pady=(5,5),sticky="")

		self.name_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Name",font=("_",22),width=450,height=35,border_color="Gray70")
		self.name_entry.grid(row=2,column=1,padx=50,pady=(5,5),sticky="")


		self.done_button = ctk.CTkButton(self.main_frame,text="Save",command=self.done_event,font=("_",25,"bold","italic"),fg_color="Gray15",hover_color="Gray24",height=35,border_color="Gray70",border_width=2,width=450)
		self.done_button.grid(row=3,column=1,padx=50,pady=(5,15),sticky="")


		self.after(50,self.lift)
		self.lift()

	def set_directory_event(self):
		directory = filedialog.askdirectory()
		if directory == None: directory = "Choose Directoy"
		self.directory = directory
		self.change_directory.configure(text=self.directory,font=("_",12))
		self.after(1,self.lift())

	def done_event(self):
		name = self.name_entry.get()
		print("Direc",self.directory)
		self.create_pallet_event(name,self.directory)
		self.destroy()
		




class App(ctk.CTk):
	def __init__(self):
		super().__init__()
		ctk.set_appearance_mode("dark")
		# Configure Window
		self.title("Colour picker")
		self.geometry(f"{1100}x{580}")

		# Configure grid layout (4x4)
		self.grid_columnconfigure((1), weight=1)
		self.grid_columnconfigure((2), weight=0)
		self.grid_rowconfigure((0), weight=1)
		self.grid_rowconfigure((1), weight=0)

		self.appearance = "Dark"
		self.folder_path = self.search_folder()

		# load files(images and modes and configs)
		image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Files")

		self.home_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
		self.art_pallet_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "Art_Pallet_dark.png")),dark_image=Image.open(os.path.join(image_path, "Art_Pallet_light.png")), size=(20, 20))                                              
		self.settings_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "Settings_dark.png")),dark_image=Image.open(os.path.join(image_path, "Settings_light.png")), size=(20, 20))                                            
		self.right_arrow_image = ctk.CTkImage(dark_image=Image.open(os.path.join(image_path,"right-arrow_light.png")),light_image=Image.open(os.path.join(image_path,"right-arrow.png")))
		self.left_arrow_image = ctk.CTkImage(dark_image=Image.open(os.path.join(image_path,"left-arrow_light.png")),light_image=Image.open(os.path.join(image_path,"left-arrow.png")))
		self.folder = ctk.CTkImage(light_image=Image.open(os.path.join(image_path,"file-and-folder-dark.png")),dark_image=Image.open(os.path.join(image_path,"file-and-folder-dark.png")))
		self.location = None


		# Setting up Frames
		self.navigation_frame = NavigatioFrame(
			master=self, corner_radius=0, 
			home_button_event=self.home_button_event,
			art_pallet_image=self.art_pallet_image,
			settings_image=self.settings_image,
			home_image=self.home_image, 
			settings_button_event = self.settings_button_event, 
			colours_button_event = self.colours_button_event,
			debug_command = self.debug_command,
			appearance_main = self.appearance_main

			)
		

		self.home_frame = HomeFrame(master=self,corner_radius=0,fg_color="transparent", quit_event=self.quit_event)
		# Its only pressed in grid when button pressed see select_frame_by_name

		self.settings_frame = SettingsFrame(master=self,corner_radius=0,fg_color="transparent")
		# Its only pressed in grid when button pressed see select_frame_by_name


		self.colour_frame = ctk.CTkFrame(self, corner_radius=6)
		self.colour_frame.grid_rowconfigure(0,weight=1)
		self.colour_frame.grid_rowconfigure(1,weight=0)
		self.colour_frame.grid_columnconfigure((0),weight=1,minsize=260)
		self.colour_frame.grid_columnconfigure((1,2),weight=0)


		self.colour_frame_pallet = ColourFramePallet(
			master=self.colour_frame, corner_radius=6, 
			left_arrow_image=self.left_arrow_image,
			right_arrow_image=self.right_arrow_image,
			update_preview_image = self.update_preview_image,
			gradient_length = self.gradient_length,
			)
		self.colour_frame_pallet.grid(row=0, column=1, padx=10, pady=20, sticky="nswe")
		
		self.colour_frame_preview = ColourFramePreview(master=self.colour_frame,create_pallet_event=self.create_pallet_event,folder_path = self.folder_path, corner_radius=6)
		self.colour_frame_preview.grid(row=0, column=0, padx=10, pady=20, sticky="nswe")

		self.colour_frame_settings = ColourFrameSettings(master=self.colour_frame, corner_radius=6, colour_frame_pallet=self.colour_frame_pallet)
		self.colour_frame_settings.grid(row=0, column=2, padx=10, pady=20, sticky="nswe")

		self.navigation_frame.colour_frame_pallet_inst = self.colour_frame_pallet
		self.navigation_frame.grid(row = 0,column = 0, sticky="nsew")


		

		# Set Defaults
		
		self.select_frame_by_name("home")
		self.search_folder()

	def home_button_event(self):
		self.select_frame_by_name("home")

	def settings_button_event(self):
		self.select_frame_by_name("settings")

	def colours_button_event(self):
		self.select_frame_by_name("colour")

	def appearance_main(self,new = None):
		if new:
			print("appearance")
			self.appearance = new
			ColourFrameSettings.get_appearance(new)

	def ask_appearance(self):
		return self.appearance

	def create_pallet_event(self,name,location):
		#location = self.search_folder()if self.search_folder() else location
		print(location)
		self.colour_frame_pallet.save_pallet(location,name)

	def gradient_length(self):
		value = ColourFrameSettings.gradient_length(self)
		return value

	def update_preview_image(self,image):
		new_image = image
		self.colour_frame_preview.update(new_image)

	def debug_command(self):
		print("Fuck")
		self.colour_frame_pallet.printarray()
	
	def select_frame_by_name(self, name):



		# Highligtes the Pressed Button
		if name == "home": 
			self.navigation_frame.highlite_buttons("home_button", "gray20") 
			self.home_frame.grid(row = 0,column = 1,sticky="nsew")	
		else: 
			self.home_frame.grid_forget()
			

		if name == "colour": 
			self.navigation_frame.highlite_buttons("colours_button", "gray20")
			self.colour_frame.grid(row=0, column=1, sticky="nsew")
		else:
			self.colour_frame.grid_forget()
			
		if name == "settings": 
			self.navigation_frame.highlite_buttons("settings_button", "gray20")
			self.settings_frame.grid(row=0, column=1, sticky="nsew")
		else:
			self.settings_frame.grid_forget() 
	
	def set_settings(self,array):
		self.settings = array

	def search_folder(self):
		username = getpass.getuser()

		# Construct the path to AppData\Roaming
		appdata_path = os.path.join("C:\\", "Users", username, "AppData", "Roaming", "SoundSpacePlus", "colorsets")

		# Check if the folder exists
		if os.path.exists(appdata_path):
			return(appdata_path)
		else:
			return None






	def quit_event(self):
		print("Quit")
		self.destroy()
		
def main():
    app = App()
    app.mainloop()
	
if __name__ == "__main__":
    main()


