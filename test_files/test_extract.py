from esg_data.extractor import process_pdf_extract, save_extracted_to_csv

pdf_path = "test_files/Bayer_2021_esg.pdf"
results = process_pdf_extract(pdf_path)
save_extracted_to_csv(results, pdf_path)
