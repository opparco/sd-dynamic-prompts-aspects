import os
import modules.scripts as scripts
from modules.processing import StableDiffusionProcessing

import gradio as gr

basedir = scripts.basedir()


class Script(scripts.Script):

    def __init__(self):
        self.aspects_file_mtime = 0
        self.aspects = {}

        self.load_aspects_from_file()

    def title(self):
        return "Dynamic Prompts Aspects"

    def show(self, is_img2img: bool):
        return scripts.AlwaysVisible

    def ui(self, is_img2img: bool):
        with gr.Group(elem_id="dynamic-aspects"):
            with gr.Accordion("Dynamic Prompts Aspects", open=False):
                enabled = gr.Checkbox(
                    label="Enabled",
                    value=True,
                    elem_id="dynamic-aspects-enabled",
                )
        return [enabled]

    def load_aspects_from_file(self):
        aspects_file = os.path.join(basedir, "aspects.txt")

        if os.path.exists(aspects_file):
            mtime = os.path.getmtime(aspects_file)
            # print("Dynamic aspects aspects.txt mtime: {}.".format(mtime))
            if mtime == self.aspects_file_mtime:
                return  # not modified.

            self.aspects_file_mtime = mtime
            self.aspects.clear()
            with open(aspects_file, encoding="utf8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    keyword, aspect = line.split()
                    width, height = [int(i) for i in aspect.split('x')]
                    self.aspects[keyword] = (width, height)
                    # print("Dynamic aspects {0} {1}x{2}".format(keyword, width, height))

    def apply_aspect(self, p: StableDiffusionProcessing, prompt: str):
        for keyword, aspect in self.aspects.items():
            if keyword in prompt:
                p.width, p.height = aspect
                break

    def process(self, p: StableDiffusionProcessing, enabled: bool):

        if not enabled:
            # print("Dynamic aspects disabled.")
            return

        self.load_aspects_from_file()

        for prompt in p.all_prompts:
            self.apply_aspect(p, prompt)
