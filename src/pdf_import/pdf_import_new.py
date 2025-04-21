def run_pdf_import_gui():
    """
    启动 PDF 导入 GUI，返回导入成功的 PDF 文件绝对路径（失败则返回 None）
    """
    import os
    import shutil
    import pandas as pd
    from tkinter import Tk, Button, Label, Entry, StringVar, filedialog, messagebox
    from datetime import datetime
    import logging

    # ================= 日志设置 =================
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_dir = os.path.join(BASE_DIR, "log")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "pdf_extract_text_and_tables.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    # 构建绝对路径
    TARGET_FOLDER = os.path.join(BASE_DIR, "data", "esg_reports_pdf")
    EXCEL_FILE = os.path.join(TARGET_FOLDER, "import records.xlsx")
    imported_path = {"path": None}  # ✅ 用于保存导入成功的路径

    def select_pdf_file():
        file_path = filedialog.askopenfilename(
            title="choose PDF file",
            filetypes=[("PDF file", "*.pdf")]
        )
        if file_path:
            source_var.set(file_path)

    def move_pdf():
        source_path = source_var.get()
        if not os.path.isfile(source_path):
            messagebox.showerror("error", f"file {source_path} no existence！")
            logging.warning(f"尝试导入不存在的文件: {source_path}")
            return

        os.makedirs(TARGET_FOLDER, exist_ok=True)
        file_name = os.path.basename(source_path)
        target_path = os.path.join(TARGET_FOLDER, file_name)

        try:
            shutil.copy2(source_path, target_path)
            messagebox.showinfo("", "import successfully!")

            import_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {'file_name': [file_name], 'import_time': [import_time]}
            df = pd.DataFrame(data)

            if os.path.exists(EXCEL_FILE):
                existing_df = pd.read_excel(EXCEL_FILE)
                df = pd.concat([existing_df, df], ignore_index=True)

            df.to_excel(EXCEL_FILE, index=False, engine='openpyxl', sheet_name='import_records')

            imported_path["path"] = os.path.abspath(target_path)

            # ✅ 日志输出
            logging.info(f"PDF 文件导入成功: {imported_path['path']}")
            logging.info(f"导入记录写入 Excel: {EXCEL_FILE}")

            root.destroy()
        except Exception as e:
            messagebox.showerror("import_false", str(e))
            logging.error(f"导入失败: {e}")

    root = Tk()
    root.title("PDF file manage tool")
    root.geometry("500x150")
    source_var = StringVar()

    Label(root, text="choose PDF file:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    Entry(root, textvariable=source_var, width=40).grid(row=0, column=1, padx=10, pady=10)
    Button(root, text="browse", command=select_pdf_file).grid(row=0, column=2, padx=10, pady=10)
    Button(root, text="import file", command=move_pdf, width=20).grid(row=1, column=1, pady=20)

    root.mainloop()
    return imported_path["path"]  # ✅ 返回导入成功的 PDF 文件路径（或 None）
