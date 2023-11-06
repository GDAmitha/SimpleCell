from rxconfig import config
from typing import List
import re
import reflex as rx
from backend import cellClassifier, cellClassifier3
#cellClassifier2

color1 = "rgb(102,199,244)"
#color1 = "#0E79B2"
color2 = "#FBFEF9"


filename = f"{config.app_name}/{config.app_name}.py"
# ok so this is for the left side block...
style = {
    "color": "black",
    ".some-css-class": {
        "text_decoration": "underline",
    },
    rx.Input: {
        "color": "black", 
        "border": "1px solid black"
    },
    rx.Select: {
        "color": "black", 
        "border": "1px solid black"
    },
    rx.Text: {
        "font_family": "Comic Sans MS",
        "color": "black", 
    },
    rx.Divider: {
        "margin_bottom": "3em", 
        "margin_top": "0.5em",  
    },
    rx.Heading: {
        "font_weight": "500",  
        "color": "black",  
    },
}

class State(rx.State):
    
        
    show: bool = False

    
    #EmbeddedList: List[cellClassifier.ClassifiedCell]
    EmbeddedList: List[str]
    outputList : List[str]
    def change(self):
        self.processing, self.complete = True, False

    async def uploadHandler(self, files: list[rx.UploadFile]):
        self.change()
        # yield
        
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_asset_path(file.filename)
            with open(outfile, "wb") as file_object:
                file_object.write(upload_data)
            #self.outputList.append("Cell Type:")
            self.outputList.append(cellClassifier.cellClassifierFunc(outfile))
            self.EmbeddedList.append(cellClassifier3.cellClassifierFunc(outfile))
            #self.EmbeddedList.append(cellClassifier2.cellClassifierFunc2(outfile))
        self.processing = self.change()
    
    def generate_GPT(self):
        for i in self.EmbeddedList:
            print(i)
    

    
            


#topbar design...
def navbar():
    return rx.vstack(
        rx.markdown("## SimpleCell"),
        bg="#d3d3d3",
        color="black",
        margin="auto",
        position="fixed",
        top="0px",
        z_index="5",
        width="100%",
        border_bottom="1px solid black"
    )

def generate_GPT_form():

        return rx.vstack(
                rx.heading(
                    "More Information:"
                ),
                rx.foreach(
                    State.EmbeddedList, show_info
                ),
                
                color = 'black',
                bg = '#FBFEF9',
                size = '30px',
                height = "100%",
                margin = "20px",
                padding = "30px",
                align_items="top",
                width = "100%",
                radius = "10px",
                border = "3px solid black",
                border_radius= "lg",
            )

def show_value(value):
    return rx.vstack(
        rx.text(value, font_size="15px", ),
       
        bg = '#eeeee4',
        width = "225px",
        height = "50px",
        margin = "50px",
        padding = "50px",
        # color = rx.cond(
        #     value.error < 50,
        #     "green",
        #     "orange",
        # ),
        border = "1px solid black",
        border_radius = "md"
    )
def show_info(value):
    return rx.vstack(
        rx.text(value, font_size="10px", ),
       
        bg = '#eeeee4',
        width = "225px",
        height = "50px",
        margin = "50px",
        padding = "50px",
        
        border = "1px solid black",
        border_radius = "md"
    )
def show_celltype():
    return rx.vstack(
        rx.heading(
            "The cell you're dealing with is:",
        ),
        rx.foreach(
            State.outputList, show_value
        ),
        
        rx.button(
            "Get More Information",
            bg="#fef2f2",
            color="#b91c1c",
            border_radius="lg",
            on_click=State.generate_GPT(),
        ),

        color = 'black',
        bg = '#FBFEF9',
        size = '30px',
        height = "100%",
        margin = "20px",
        padding = "30px",
        align_items="top",
        width = "100%",
        radius = "10px",
        border = "3px solid black",
        border_radius= "lg",
    )


def uploadingfunction():
    """The main view."""
    return rx.vstack(
        rx.upload(
            rx.vstack(
                rx.heading("Data Input", size="lg", margin="10px"),
            
                rx.button(
                    "Select .h5ad File",
                    color = color1,
                    bg="twitter",
                    border=f"1px solid {color1}",
                ),
                rx.text(
                    "Drag and drop files here or click to select files."
                ),
            ),
            multiple=True,
            accept={
                "sequencing/h5ad": [".h5ad"]
            },
            max_files=5,
            disabled=False,
            on_keyboard=True,
            border=f"1px solid {color1}",
            padding="5em",
        ),
        rx.button(
            "Upload",
            on_click=lambda: State.uploadHandler(
                rx.upload_files()
            ),
        ),
        color = 'black',
        bg = '#FBFEF9',
        size = '30px',
        height = "100%",
        margin = "20px",
        padding = "30px",
        align_items="top",
        width = "100%",
        radius = "10px",
        border = "3px solid black",
        border_radius= "lg",
    )

#Final page design
@rx.page(title='SimpleCell')
def index():
    return rx.vstack(
        navbar(),
        rx.hstack(
            uploadingfunction(),
            rx.hstack(
                 show_celltype(),
                # show_cellGPT(),
                overflow = 'hidden',
                width = "100%",
            ),
            width="100%"
        ),
        padding_top ="5em",
        width ="100%",
        color="black"
    )


# app = rx.App(style=style)
app = rx.App(style=style)
app.add_page(index)
app.compile() 
