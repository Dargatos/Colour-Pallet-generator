import tkinter as tk
import customtkinter as ctk
import os
from CTkColorPicker import *
from PIL import Image, ImageTk
from Pallet_generator import *
from ctk_color_picker import *


WSDefaultx = 1100
WSDefaulty = 580



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
			command=None,
			**kwargs
			):
		super().__init__(master, **kwargs)
		self.grid_rowconfigure(5, weight=1)
		

		
		self.debug_command = debug_command
		self.home_button_event = home_button_event
		self.colours_button_event = colours_button_event
		self.settings_button_event = settings_button_event
		self.art_pallet_image = art_pallet_image
		self.settings_image = settings_image
		self.home_image = home_image


		self.navigation_frame_logo_label = ctk.CTkLabel(self,text=" Colour Generator", compound="left",font=ctk.CTkFont(size=15, weight="bold"))
		self.navigation_frame_logo_label.grid(row=0, column=0, padx=20, pady=20)   

		self.home_button = ctk.CTkButton(
			self, 
			corner_radius=0,
			height=40, 
			border_spacing=10, 
			text="Home",
			fg_color="transparent", 
			text_color=("_", "White"),
			hover_color=("_", "gray20"), 
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
			text_color=("_", "White"),
			hover_color=("_", "gray20"), 
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
			text_color=("_", "White"),
			hover_color=("_", "gray20"), 
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
			text_color=("_", "White"),
			hover_color=("_", "gray20"), 
			anchor="w",
			command=self.debug_command
			)
		self.extra_button.grid(row = 4, column = 0, sticky = "nsew")
        
		self.last_button = None

	def highlite_buttons(self, button_name, fg_color):
		
		
		if self.last_button: self.last_button.configure(fg_color="transparent")
		
		button = getattr(self, f"{button_name}", None)
		if button: button.configure(fg_color=fg_color)
		self.last_button = button
		
	
class ColourFrameSettings(ctk.CTkFrame):
	def __init__(self,master,colour_frame_pallet, **kwargs):
		super().__init__(master, **kwargs)
		
		self.colour_frame_pallet = colour_frame_pallet

		self.checkbox_var = tk.StringVar()
		self.rowconfigure((0), weight=0)
		self.rowconfigure((1,2,3,4), weight=0)

		self.label_colour_settings = ctk.CTkLabel(self, corner_radius=50, text="Colour Settings", font=("_",20,"bold"), anchor="w")
		self.label_colour_settings.grid(row=0, column=0, sticky="swen", padx=10, pady=4)

		self.gradient_button = ctk.CTkCheckBox(self, text="gradient")
		self.gradient_button.grid(row=1, column=0,sticky="nsew", padx=15, pady=4)

		self.multiple_pallets_button = ctk.CTkCheckBox(self, text="Alternate Color Themes",onvalue="On",offvalue="Off",command=self.button_clicked,variable=self.checkbox_var)
		self.multiple_pallets_button.grid(row=2, column=0, sticky="nswe", padx=15, pady=4)

	def button_clicked(self):
		current_value = self.checkbox_var.get()
		self.colour_frame_pallet.multiple_pallets_button(current_value)


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


class SettingsFrame(ctk.CTkFrame):
	def __init__(self,master, **kwargs):
		super().__init__(master, **kwargs)

		self.grid_rowconfigure((0,1),weight=0)

		self.setting_frame_bt1 = ctk.CTkButton(self,text="bt1")
		self.setting_frame_bt1.grid(row=0, column=0)
		self.setting_frame_bt2 = ctk.CTkButton(self,text="bt2")
		self.setting_frame_bt2.grid(row=1, column=0)


class ColourFramePallet(ctk.CTkFrame):
	def __init__(self,master,debug_array,right_arrow_image,left_arrow_image,update_preview_image, **kwargs):
		super().__init__(master, **kwargs)

		self.grid_rowconfigure((0,2),weight=0)
		self.grid_rowconfigure((1),weight=1)		
		self.grid_columnconfigure((0,1,2),weight=0)

		self.update_preview_image = update_preview_image
		self.right_arrow_image = right_arrow_image
		self.left_arrow_image = left_arrow_image



		self.colour_buttons_list_parent = []
		self.colours_list_frame_array = []
		self.colour_buttons_list = []
		self.button_id = None
		self.last_fg_color = None
		self.current_pallet = 0
		self.current_frame = None

	
		self.debug_array = debug_array

		self.label_colour_pallet = ctk.CTkLabel(self, corner_radius=0, text=f'{"Color Pallet"} {self.current_frame}',font=("_",20,"bold"),fg_color="transparent",width=10)
		self.label_colour_pallet.grid(row=0, column=0, columnspan=3, sticky="nswe", padx=20, pady=(10,0))


		self.next_pallet_button= ctk.CTkButton(self, corner_radius=6,fg_color="Gray20",text="",height=20,width=20, hover_color="Gray25",image=right_arrow_image,command=lambda: self.change_frame(1))
		#self.next_pallet_button.grid(row=0,column=2,sticky="",pady=(10,0),padx=(10,0))
		
		self.previous_pallet_button= ctk.CTkButton(self, corner_radius=6,fg_color="Gray20",text="",height=20,width=20, hover_color="Gray25",image=left_arrow_image,command=lambda: self.change_frame(-1))
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

		self.add_colour_list_frame(0)
		self.bind("<Configure>", self.hide_scrollbar)


	def printarray(self):
		current_frame_index = self.colours_list_frame_array.index(self.current_frame)
		button_list = self.colour_buttons_list_parent[current_frame_index]
		temp_array = []
		for button in button_list:
			color = button.cget("fg_color")
			temp_array.append(color)
		print(f'{"Array"}{current_frame_index + 1}{temp_array}')
		

	def multiple_pallets_button(self,value):
		
		if value == "On":
			self.next_pallet_button.grid(row=0,column=2,sticky="",pady=(10,0),padx=(10,0))
			self.previous_pallet_button.grid(row=0,column=0,sticky="",pady=(10,0),padx=(0,10))
		else:
			self.next_pallet_button.grid_forget()
			self.previous_pallet_button.grid_forget()
		
	def add_colour_list_frame(self,pos):
		#Creates frame when called
		frame = ctk.CTkScrollableFrame(self.colour_list_parent, corner_radius=0, scrollbar_button_color="Gray17")
		frame.grid_columnconfigure(0,weight=1)
		frame.configure()

		#Saves frame in 
		colour_array = []

		self.colour_buttons_list_parent.append(colour_array)

		self.colours_list_frame_array.append(frame)
		self.place_frame(frame)
		
	def update(self):
		current_frame_index = self.colours_list_frame_array.index(self.current_frame)
		colors = self.colour_buttons_list_parent[current_frame_index]
		temp_array = []
		for button in colors:
			color = button.cget("fg_color")
			temp_array.append(color)
		color_gen = ColorGenerator()		
		image = color_gen.create_color_image(temp_array)
		self.update_preview_image(image)

	def save_pallet(self,place,name):
		print("")
		# add save location

		print("Shit")
	def change_frame(self,where):
		
		
		current_frame_place = self.colours_list_frame_array.index(self.current_frame) +1
		current_array = self.colour_buttons_list_parent[current_frame_place-1]

		print(f'{self.current_frame} {self.colours_list_frame_array[current_frame_place-1]}')
		print(len(current_array))


		if len(current_array)==0:
			print("Destroy")
			self.current_frame.destroy()
			self.colours_list_frame_array.remove(self.current_frame)

		if len(self.colours_list_frame_array) <= current_frame_place + where -1:
			self.add_colour_list_frame(current_frame_place)
		else:
			frame = self.colours_list_frame_array[current_frame_place + where -1]
			self.place_frame(frame)
			self.update()

		colour_buttons_list= self.colour_buttons_list_parent[self.colours_list_frame_array.index(self.current_frame)]

		"""for i, button in colour_buttons_list:
			print("Grid")
			button.grid_forget
			button.grid(row=len(colour_buttons_list), column=0, pady=5,sticky="nswe")"""
		
	def place_frame(self, frame):
		frame.grid(row=0, column=0,sticky="nswe")
		self.current_frame = frame
		self.label_colour_pallet.configure(text=f'{"Colour Pallet"} {self.colours_list_frame_array.index(frame)+1}')
		for i ,item in enumerate(self.colours_list_frame_array):		
			if item != frame:
				item.grid_forget()
	

	def AskColor(self):
		AskColor(command=self.add_color)
		 # open the color picker


	def add_color(self,color):
		
		colour_buttons_list = self.colour_buttons_list_parent[self.colours_list_frame_array.index(self.current_frame)]
		

		darker_color = self.darken_color(color)#calls function to make a darker version of color
		colours_list_frame = self.current_frame
		# Creates button and places it
		button = ctk.CTkButton(colours_list_frame, text=f"{color}", font=("_",15,"bold"), text_color="Black", corner_radius=6,fg_color=color,hover_color=darker_color)
		button.grid(row=len(colour_buttons_list), column=0, pady=5,sticky="nswe")
		button.configure(command=lambda btn=button: self.colour_choosen(btn,"change"))

		# save button in array
		
		colour_buttons_list.append(button)
		self.update()
		self.after(10, lambda: self.hide_scrollbar("<Configure>"))


		

	def colour_choosen(self, id, change):
		self.change = change
		if change == "change": 

			if self.button_id != None: 
				self.button_id.configure(fg_color=self.last_fg_color,font=("_",15,"bold"))

			self.button_id = id
			hover_color = id.cget("hover_color")
			self.last_fg_color = id.cget("fg_color")
			id.configure(fg_color=hover_color,font=("_",15,"bold","underline"))

		if change == "delete":self.delete_color(self.button_id)
		if change == "edit":self.edit_button(self.button_id)
		
	def delete_color(self, item):
        # Find the index of the button in the list
		colour_buttons_list = self.colour_buttons_list_parent[self.colours_list_frame_array.index(self.current_frame)]
		last = colour_buttons_list[-1]
		

		# if Button was Pressed delet last pressed button
		if item != None: 
			item.destroy()

			colour_buttons_list.remove(item)
			self.button_id = None
		
		# if Button wasnt pressed delet last button in list
		else:

			last.destroy()
			colour_buttons_list.remove(last)

		self.hide_scrollbar("<Configure>")
		self.update()
			
	def edit_button(self, button):
		
		if button:
			pick_color = AskColor() # open the color picker
			color = pick_color.get() # get the color string


			darker_color = self.darken_color(color)
			button.configure(fg_color=color,hover_color=darker_color)
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
	def __init__(self,master, **kwargs):
		super().__init__(master, **kwargs)

		

		


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
		self.create_final_pallet = CreateFinalPallet(master=self)

	def update(self,image):
		self.preview_image = image
		self.resize()
		

	def resize(self, event=None):
		
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
	def __init__(self, master, **kwargs):
		super().__init__(master, **kwargs)
		self.title("Create Pallet")
		self.geometry("500x300+300+300")
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		screen_width = self.winfo_screenwidth()
		screen_height = self.winfo_screenheight()

		x_coordinate = (screen_width - 500) // 2
		y_coordinate = (screen_height - 200) // 2

		self.main_frame = ctk.CTkFrame(self,fg_color="transparent")
		self.main_frame.grid(row=0,column=0,sticky="nswe")
		self.main_frame.grid_rowconfigure((0),weight=0)
		self.main_frame.grid_rowconfigure((1,2),weight=1)
		self.main_frame.grid_columnconfigure(1,weight=1)

		self.name_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Pallets Name",font=("_",30),width=200)
		self.name_entry.grid(row=1,column=1,padx=150,pady=(15,5),sticky="sew")

		self.done_button = ctk.CTkButton(self.main_frame,text="Done",command=self.done_event,font=("_",30,"bold","italic"),fg_color="Gray25",hover_color="Gray30")
		self.done_button.grid(row=2,column=1,padx=150,pady=(5,15),sticky="new")
		self.attributes("-topmost", True)

	def done_event(self):
		print(self.name_entry.get())
		




class App(ctk.CTk):
	def __init__(self):
		super().__init__()
	
		# Configure Window
		self.title("Colour picker")
		self.geometry(f"{WSDefaultx}x{WSDefaulty}")

		# Configure grid layout (4x4)
		self.grid_columnconfigure((1), weight=1)
		self.grid_columnconfigure((2), weight=0)
		self.grid_rowconfigure((0), weight=1)
		self.grid_rowconfigure((1), weight=0)
	

		# load files(images and modes and configs)
		image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Files")

		self.home_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
		self.art_pallet_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "Art_Pallet_dark.png")),dark_image=Image.open(os.path.join(image_path, "Art_Pallet_light.png")), size=(20, 20))                                              
		self.settings_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "Settings_dark.png")),dark_image=Image.open(os.path.join(image_path, "Settings_light.png")), size=(20, 20))                                            
		self.preview_test_image = ctk.CTkImage(Image.open(os.path.join(image_path, "Preview_test.png")))
		self.original_image = Image.open(os.path.join(image_path, "Preview_test.png"))
		self.right_arrow_image = ctk.CTkImage(dark_image=Image.open(os.path.join(image_path,"right-arrow_light.png")),light_image=Image.open(os.path.join(image_path,"right-arrow.png")))
		self.left_arrow_image = ctk.CTkImage(dark_image=Image.open(os.path.join(image_path,"left-arrow_light.png")),light_image=Image.open(os.path.join(image_path,"left-arrow.png")))



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
			debug_array=self.Debug_array,
			left_arrow_image=self.left_arrow_image,
			right_arrow_image=self.right_arrow_image,
			update_preview_image = self.update_preview_image,
			)
		self.colour_frame_pallet.grid(row=0, column=1, padx=10, pady=20, sticky="nswe")
		
		self.colour_frame_preview = ColourFramePreview(master=self.colour_frame, corner_radius=6)
		self.colour_frame_preview.grid(row=0, column=0, padx=10, pady=20, sticky="nswe")

		self.colour_frame_settings = ColourFrameSettings(master=self.colour_frame, corner_radius=6, colour_frame_pallet=self.colour_frame_pallet)
		self.colour_frame_settings.grid(row=0, column=2, padx=10, pady=20, sticky="nswe")

		self.navigation_frame.colour_frame_pallet_inst = self.colour_frame_pallet
		self.navigation_frame.grid(row = 0,column = 0, sticky="nsew")


		

		# Set Defaults
		self.select_frame_by_name("home")

	def home_button_event(self):
		self.select_frame_by_name("home")
		print("home button pressed !!")

	def settings_button_event(self):
		self.select_frame_by_name("settings")

	def colours_button_event(self):
		self.select_frame_by_name("colour")

	def Debug_array(self,array):
		print(array)

	def create_pallet_event(self,name):
		location = self.location
		self.colour_frame_pallet.save_pallet(location,name)


	def update_preview_image(self,image):
		print("preview")
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




	def quit_event(self):
		print("Quit")
		self.destroy()

if __name__ == "__main__":
		app = App()
		app.mainloop()


