import flet as ft

def main(page: ft.Page):
    page.title = "Flet_Sample"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)
    page.update()

    status_text = ft.Text()
    plot_container = ft.Container(visible=False)
    
    page.add(
        ft.ElevatedButton("File Select", on_click=lambda _: file_picker.pick_files(allowed_extensions=["txt"])),
        status_text,
        plot_container
    )
    
    page.add(
        ft.ElevatedButton("Folder Chose", on_click=lambda _: file_picker.get_directory_path()),
        status_text,
        plot_container
    )

def on_dialog_result(e: ft.FilePickerResultEvent):
    if e.files:
        print("Selected files:", e.files[0].path)
        print("Selected files:", e.files[0].name)
        print("Selected file or directory:", e.path)

ft.app(main)
