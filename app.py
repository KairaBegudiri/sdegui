import gi
import subprocess
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class SafeDeleteApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Safe Eraser")
        self.set_border_width(10)
        self.set_default_size(400, 200)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        self.disk_store = Gtk.ListStore(str)
        self.populate_disks()
        self.combo = Gtk.ComboBox.new_with_model(self.disk_store)
        renderer_text = Gtk.CellRendererText()
        self.combo.pack_start(renderer_text, True)
        self.combo.add_attribute(renderer_text, "text", 0)
        vbox.pack_start(self.combo, False, False, 0)

        self.delete_button = Gtk.Button(label="Safe Delete")
        self.delete_button.connect("clicked", self.on_safe_delete)
        vbox.pack_start(self.delete_button, False, False, 0)

        self.status_label = Gtk.Label(label="")
        vbox.pack_start(self.status_label, False, False, 0)

    def populate_disks(self):
        result = subprocess.run(["lsblk", "-d", "-n", "-o", "NAME"], capture_output=True, text=True)
        for disk in result.stdout.splitlines():
            self.disk_store.append([f"/dev/{disk}"])

    def on_safe_delete(self, button):
        tree_iter = self.combo.get_active_iter()
        if tree_iter is None:
            self.status_label.set_text("Lütfen bir disk seçin!")
            return
        disk = self.disk_store[tree_iter][0]
        self.status_label.set_text(f"{disk} üzerinde işlem başlatıldı...")
        GLib.idle_add(self.safe_delete_disk, disk)

    def safe_delete_disk(self, disk):
        try:
            subprocess.run(["sudo", "shred", "-v", "-n", "1", disk], check=True)

            subprocess.run(["sudo", "mkfs.ext4", "-F", disk], check=True)

            self.status_label.set_text(f"{disk} güvenli şekilde temizlendi!")
        except subprocess.CalledProcessError as e:
            self.status_label.set_text(f"Hata oluştu: {e}")

        return False

win = SafeDeleteApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
