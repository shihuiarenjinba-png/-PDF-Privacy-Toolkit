# Microsoft Store掲載文｜PDF Privacy Toolkit｜レビュー準備稿
対象ブランチ: `ui/safe-product-upgrade-20261019`
状態: **文案完成 / 公開未承認 / Store ID・価格の実入力未済**
価格の仮設定: **無料候補（仮）**。正式価格・対応市場は権限のある販売者が承認し、Partner Centerで指定する。

## ja-JP
**製品名（候補）:** PDF Privacy Toolkit

**短い説明:**
PDFの結合・分割・ページ選択と、文書情報・XMPメタデータ除去を行うローカルWindowsツールです。

**詳細説明（そのまま編集欄へ転記可能）:**
PDFを選択し、ページの結合・分割・抽出または対応メタデータの除去を行って、元のファイルとは別のPDFを作成します。保存前に入力ファイルと処理内容を確認できます。

・PDFの結合・分割・指定ページ保存
・Document Info・XMPメタデータの除去
・新規ファイル出力と保存前の確認

**対応範囲と重要な注意事項:**
本文、画像、注釈、フォーム、添付ファイルに含まれる秘密情報の完全削除には対応しません。文書情報を消したPDFが匿名化されたとみなさないでください。

**What's new:** 初回提出時は空欄。製品更新の場合のみ新旧の違いを事実確認して記載。

## en-US
**Suggested title:** PDF Privacy Toolkit

**Short description:**
Merge, split or select PDF pages and remove supported document metadata while preserving the original files.

**Full description:**
Process PDF files locally: merge multiple documents, split pages, save a selected page range or remove supported Document Info and XMP metadata. Review the operation before creating a new output file.

• Merge, split and select PDF pages
• Remove supported Document Info and XMP metadata
• Preview the operation before separate-file export

**Important limitations:**
Does not redact sensitive text, images, annotations, forms or attachments. Removing metadata does not make a PDF anonymous or safe to share.

**What's new:** Leave blank for the initial submission.

## Partner Center 編集チェック
- 描写の対象は各製品の現行ブランチで**実装が確認できる機能のみ**。未知の機能や完全安全保証を足さない。
- 正式名の重複確認、年齢区分質問票、価格、カテゴリ、地域、検索キーワード、機能欄は提出画面で設定する。価格は購入実績の裏付けがない仮説。
- スクリーンショットは実機撮影5枚。本文に外部URL、HTML、未確認の商標や第三者との提携表現を入れない。
- 最終チェック: ユーザー向けの日本語/英語を実画面と照合。英語UIが未合格なら対応言語を無理に追加しない。
- ソースWindows QA、MSIX、Store Identity、プライバシー・サポート情報、ライセンス承認が揃うまで掲載しない。

公式: https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/add-and-edit-store-listing-info
