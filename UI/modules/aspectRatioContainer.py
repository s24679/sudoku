from customtkinter import CTkFrame

class AspectRatioContainer(CTkFrame):
    def __init__(self, master, aspect_ratio=16/9, widget_class=CTkFrame, **widget_kwargs):
        super().__init__(master)
        self.aspect_ratio = aspect_ratio
        self.inner_widget = widget_class(self, **widget_kwargs)
        self.inner_widget.place(x=0, y=0)
        self.bind("<Configure>", self._resize_inner)

    def _resize_inner(self, event):
        container_width = self.winfo_width()
        container_height = self.winfo_height()

        desired_width = container_width
        desired_height = int(desired_width / self.aspect_ratio)

        if desired_height > container_height:
            desired_height = container_height
            desired_width = int(desired_height * self.aspect_ratio)

        x = (container_width - desired_width) // 2
        y = (container_height - desired_height) // 2

        relwidth = desired_width/container_width
        relheight = desired_height/container_height

        self.inner_widget.place(x=x, y=y, relwidth=relwidth, relheight=relheight)

    def get(self):
        return self.inner_widget
