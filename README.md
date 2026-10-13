# PDF Privacy Toolkit

機密PDFをWebサービスへアップロードせず、**ローカルで本当に削除できる情報と、単に見えなくするだけの処理を区別して扱うPDF Sanitizer**として設計します。

## 最重要方針

黒い四角を上から重ねただけの「見た目だけ墨消し」は、下の文字やobjectが残るため安全化とは扱いません。

販売版で「redacted」と呼ぶのは、以下のいずれかを満たした出力だけです。

1. PDF redaction機能で対象領域のunderlying text / vector / image contentを削除し、新PDFへ保存する。
2. Strong Flatten Modeで、redaction後ページを画像へrenderし、**新規PDFをゼロから再構築**する。

## 想定処理

- metadata / XMP / document info削除
- attachments / embedded files検査・削除
- annotations / comments検査・削除
- form fields / AcroForm検査・flattenまたは削除
- JavaScript / actions / links検査
- page削除 / 並べ替え
- true redaction
- Strong Flatten Mode
- password保護は「情報削除」とは別機能として扱う

## Redaction workflow

1. ユーザーが検索語・領域・ページを指定
2. text layerがあるPDFでは文字座標からcandidate boxを作る
3. candidateを人がPreview確認
4. redaction annotationを適用しunderlying objectを削除
5. 新規ファイルとして保存
6. 出力PDFから再度text extractionし、指定禁止語が残っていないか検査
7. metadata / attachment / annotation / form / actionを再検査
8. output SHA256とaudit reportを保存

OCRはスキャンPDFで候補位置を出す補助に限定し、**OCRが何も見つけなかったことを安全証明には使いません。** スキャンPDFではmanual reviewを必須にします。

## Strong Flatten Mode

最高安全寄りのモードでは、redaction後の各ページを高解像度画像へrenderし、brand-new PDFへ再構成します。これにより元PDFのhidden text、vector object、form、annotation、attachment、link等を引き継がない設計にします。

ただし、画像そのものに機密文字が残っていれば安全ではありません。したがってflatten前のredaction確認と、flatten後の再検査を両方行います。

## 販売上の約束

- 「黒塗りしたので安全」とは言わない
- 「OCR 100%」とは言わない
- redaction対象とmetadata sanitizationを別項目でreportする
- 未検査要素があればPASSではなくREVIEW/BLOCKにする
- 元PDFを上書きしない
- 出力hashと処理履歴を残す

法的証拠能力や完全な機密除去を保証する製品とはせず、**どの要素を削除し、何を再検査したか追跡できるローカルPDF Sanitizer**を目標にします。


## 拡張MVP: 定型PDF一括入力（2026-10）

- 目的: 既存の入力欄（AcroForm）を持つPDFに対し、CSV/XLSXの各行から1人1PDFを生成
- GUI: `python batch_form_gui.py`
- CLI: `python batch_form_filler.py template.pdf data.csv output_folder --mapping mapping.json`
- 列名対応JSON例: `{"name":"person_name","amount":"total_yen"}`
- 追加依存: `python -m pip install "pypdf>=5.9,<7" "openpyxl>=3.1,<4"`
- 検証用依存（テストのみ）: `python -m pip install reportlab`
- テスト: `python -m unittest discover -s tests -p "test_batch_form_filler.py"`
- 生成物: `filled_0001.pdf` 等、`batch_report.json`（テンプレートと元データのハッシュを記録）
- 入力とテンプレートは変更しない。出力先には毎回新しいフォルダを作成
- 制限: **テキストAcroFormのみ**。XFA/電子署名/チェックボックス/スキャンPDFへの文字貼り付け/flatten未対応
- **重要**: PDFの画面表示と印刷の確認は別途必要。特に日本語フォント埋込みは未対応のため、非ASCII文字を含む出力はREVIEW扱い。
- **重要**: 一括フォーム入力はPDFの機密削除や墨消し機能ではありません。テンプレートの既存情報やmetadataを引き継ぐ可能性があります。
- 状態: Windows実機・複数ビューワーの視覚検証・EXE化が未完了の開発MVP。販売承認済みと扱いません。
