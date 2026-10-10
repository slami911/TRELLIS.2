import os, random, shutil, threading, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from gradio_client import Client, handle_file

SPACE_ID = "microsoft/TRELLIS.2"

class TrellisDesktopApp:
    def __init__(self, root):
        self.root = root
        root.title("TRELLIS.2 Desktop")
        root.geometry("720x520")
        root.minsize(640, 470)
        self.image_path = None
        self.model_state = None
        self.busy = False

        outer = ttk.Frame(root, padding=18)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="TRELLIS.2 Desktop", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(outer, text="Create a textured 3D model from an image using the hosted TRELLIS.2 service.", wraplength=670).pack(anchor="w", pady=(3, 14))

        row = ttk.Frame(outer); row.pack(fill="x")
        self.image_label = ttk.Label(row, text="No image selected")
        self.image_label.pack(side="left", fill="x", expand=True)
        self.pick_button = ttk.Button(row, text="Choose image…", command=self.choose_image)
        self.pick_button.pack(side="right")

        settings = ttk.LabelFrame(outer, text="Generation settings", padding=12)
        settings.pack(fill="x", pady=14)
        ttk.Label(settings, text="Resolution").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=5)
        self.resolution = tk.StringVar(value="512")
        ttk.Combobox(settings, textvariable=self.resolution, values=("512", "1024", "1536"), state="readonly", width=12).grid(row=0, column=1, sticky="w", pady=5)
        ttk.Label(settings, text="Face target").grid(row=0, column=2, sticky="w", padx=(24, 8), pady=5)
        self.faces = tk.StringVar(value="100000")
        ttk.Combobox(settings, textvariable=self.faces, values=("50000", "100000", "200000", "300000", "500000"), state="readonly", width=12).grid(row=0, column=3, sticky="w", pady=5)
        ttk.Label(settings, text="Texture size").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=5)
        self.texture = tk.StringVar(value="2048")
        ttk.Combobox(settings, textvariable=self.texture, values=("1024", "2048", "4096"), state="readonly", width=12).grid(row=1, column=1, sticky="w", pady=5)
        ttk.Label(settings, text="Hugging Face token (optional)").grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 4))
        self.token = tk.StringVar()
        ttk.Entry(settings, textvariable=self.token, show="•", width=48).grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 4))
        ttk.Label(settings, text="Token stays in memory only; it is not saved to a file.", foreground="#666666").grid(row=4, column=0, columnspan=4, sticky="w")

        actions = ttk.Frame(outer); actions.pack(fill="x", pady=(0, 12))
        self.generate_button = ttk.Button(actions, text="Generate 3D model", command=self.start_generation)
        self.generate_button.pack(side="left")
        self.export_button = ttk.Button(actions, text="Export GLB…", command=self.start_export, state="disabled")
        self.export_button.pack(side="left", padx=8)
        self.progress = ttk.Progressbar(outer, mode="indeterminate"); self.progress.pack(fill="x", pady=(2, 8))
        self.status = tk.StringVar(value="Ready. Select an image to begin.")
        ttk.Label(outer, textvariable=self.status, wraplength=670).pack(anchor="w")
        ttk.Label(outer, text="Privacy: images are uploaded to the remote Hugging Face Space. Do not upload private or sensitive images. Speed and availability depend on the hosted service.", wraplength=670, foreground="#8a4b08").pack(anchor="w", side="bottom", pady=(18, 0))

    def choose_image(self):
        path = filedialog.askopenfilename(title="Choose an image", filetypes=[("Image files", "*.png *.jpg *.jpeg *.webp *.bmp"), ("All files", "*.*")])
        if path:
            self.image_path = path
            self.image_label.configure(text=os.path.basename(path))
            self.model_state = None
            self.export_button.configure(state="disabled")

    def set_busy(self, busy, message=None):
        self.busy = busy
        self.pick_button.configure(state="disabled" if busy else "normal")
        self.generate_button.configure(state="disabled" if busy else "normal")
        self.export_button.configure(state="disabled" if busy or self.model_state is None else "normal")
        self.progress.start(12) if busy else self.progress.stop()
        if message: self.status.set(message)

    def client(self):
        token = self.token.get().strip()
        return Client(SPACE_ID, hf_token=token or None, verbose=False)

    def start_generation(self):
        if self.busy: return
        if not self.image_path or not os.path.isfile(self.image_path):
            messagebox.showwarning("Choose an image", "Please choose a local image first."); return
        self.set_busy(True, "Connecting to the hosted service and generating the model…")
        threading.Thread(target=self.generate_worker, daemon=True).start()

    def generate_worker(self):
        try:
            client = self.client()
            result = client.predict(
                handle_file(self.image_path), random.randint(0, 2147483647), self.resolution.get(),
                7.5, 0.7, 12, 5.0, 7.5, 0.5, 12, 3.0, 1.0, 0.0, 12, 3.0,
                api_name="/image_to_3d")
            state = result[0] if isinstance(result, (list, tuple)) else result
            if not isinstance(state, dict):
                raise RuntimeError("The service returned an unexpected result; its API may have changed.")
            self.model_state = state
            self.root.after(0, self.generation_done)
        except Exception as exc:
            error = str(exc); self.root.after(0, lambda: self.operation_failed(error))

    def generation_done(self):
        self.set_busy(False, "Model generated. Choose Export GLB to save the 3D file.")
        self.export_button.configure(state="normal")
        messagebox.showinfo("Generation complete", "The model is ready to export as a GLB file.")

    def start_export(self):
        if self.busy or self.model_state is None: return
        destination = filedialog.asksaveasfilename(title="Save 3D model", defaultextension=".glb", initialfile="trellis2_model.glb", filetypes=[("GLB 3D model", "*.glb")])
        if not destination: return
        self.set_busy(True, "Extracting and downloading the GLB file…")
        threading.Thread(target=self.export_worker, args=(destination,), daemon=True).start()

    def export_worker(self, destination):
        try:
            client = self.client()
            result = client.predict(self.model_state, int(self.faces.get()), int(self.texture.get()), api_name="/extract_glb")
            candidates = result if isinstance(result, (list, tuple)) else [result]
            source = next((item for item in reversed(candidates) if isinstance(item, str) and os.path.isfile(item)), None)
            if not source:
                raise RuntimeError("No downloadable file path was returned. The Space API may have changed.")
            shutil.copy2(source, destination)
            self.root.after(0, lambda: self.export_done(destination))
        except Exception as exc:
            error = str(exc); self.root.after(0, lambda: self.operation_failed(error))

    def export_done(self, destination):
        self.set_busy(False, f"GLB saved to: {destination}")
        messagebox.showinfo("Export complete", f"3D model saved successfully:\n{destination}")

    def operation_failed(self, error):
        self.set_busy(False, "Operation failed.")
        messagebox.showerror("TRELLIS.2 service error", f"{error}\n\nThe remote Space may be sleeping, busy, or its API may have changed. Try again later or open https://huggingface.co/spaces/microsoft/TRELLIS.2")

def main():
    root = tk.Tk()
    try: ttk.Style().theme_use("vista")
    except tk.TclError: pass
    TrellisDesktopApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
