import i18n

original = getattr(i18n, "get_language", lambda: getattr(i18n, "_LANGUAGE", "en"))()
try:
    i18n.set_language("ja")
    assert i18n.translate("Add PDFs") == "PDFを追加"
    assert i18n.translate("Merge all") == "すべて結合"
    i18n.set_language("en")
    assert i18n.translate("Add PDFs") == "Add PDFs"
    assert i18n.translate("Merge all") == "Merge all"
finally:
    i18n.set_language(original)

print("PDF Privacy Toolkit bilingual UI smoke test: OK")
