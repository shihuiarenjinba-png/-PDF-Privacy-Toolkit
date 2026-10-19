# PDF Privacy Toolkit — プライバシー・サポート提出文案
Status: **本文案作成済み / 法務・最終バイナリ通信検証・販売者窓口の承認待ち**。
本案は実装済みの範囲から作成。データ収集・外部送信の有無について最終実機/最終MSIX証拠が未確認のため無条件な断定をしない。

## 日本語プライバシー説明
**製品:** PDF Privacy Toolkit

**何を扱うか:** 利用者が指定したPDF、そのページとメタデータ、出力先、任意の出力パスワード。

**利用目的:** 利用者自身が指示したファイルの確認、加工、監査、結果表示、または成果物保存のため。

**処理・通信:** ローカルPDF処理を想定。出力パスワード等の扱いと通信動作は実パッケージで最終確認する。

**保存:** 元ファイルは利用者が指定した場所に保持し、処理されたファイルや監査ログは利用者が選んだ場所へ保存する設計です。処理中にメモリやOSの一時領域を利用する場合があります。保存済み成果物の管理・共有・削除は、基本的に利用者自身が行います。

**安全性・制限:** 本文、画像、注釈、フォーム、添付ファイルに含まれる秘密情報の完全削除には対応しません。文書情報を消したPDFが匿名化されたとみなさないでください。

**外部サービス:** Microsoft Storeの配信、Windows OSやブラウザー/セキュリティ機能、ユーザーが自らアクセスするWebサイト等には、それぞれのサービス条件・プライバシー慣行が適用されることがあります。製品がそれらのサービスのデータ取り扱い全体を支配するものではありません。

**お問い合わせ:** 正式な開発者名と有効なサポート手段がPartner Centerで承認された際に、正確な問い合わせ先を登録します。サポートのために実データや秘密情報を送ることを原則要求しません。

## English privacy explanation
**Product:** PDF Privacy Toolkit

**Data handled:** User-selected input data and application settings relevant to the selected operation. Process PDF files locally: merge multiple documents, split pages, save a selected page range or remove supported Document Info and XMP metadata. Review the operation before creating a new output file.

**Purpose:** To perform the local processing, inspection, preview, export or evidence capture requested by the user.

**Processing and transmission:** The intended processing is local to the user's device. The absence of any network transmissions in the final packaged binary must still be verified before publication.

**Storage:** The app reads files selected by the user and may process data in memory or temporary OS locations. Reports or new output files are written to locations chosen by the user. Users control the storage, sharing and deletion of their exported files.

**Limitations:** Does not redact sensitive text, images, annotations, forms or attachments. Removing metadata does not make a PDF anonymous or safe to share.

**Support:** The verified publisher's support contact will be supplied through the actual Microsoft Store listing. Customers should not send sensitive original files, passwords or tokens as part of routine support requests.

## 運用側の未完了承認（公表前に必須）
- [ ] 最終MSIXと実行EXEのネットワーク接続、ログ/クラッシュダンプ/一時ファイル、データ保持・削除を実機で監査し本文と一致させる
- [ ] 開発者の正式販売主体・問い合わせ窓口・地域別法令・責任範囲を承認
- [ ] Web Archiverは接続先、IPアドレス/HTTPヘッダー等のWebサイト側の取り扱いを正確に説明する
- [ ] Microsoft Storeの「個人情報へのアクセス/取得/送信」の質問に実際のコード/権限に従って回答。必要ならプライバシー文面を直接登録できる（公表済みURLは必須ではない）
- [ ] 日本語・英語で記載の齟齬がないか最終確認する

**現在の文案は公開用最終承認ではありません。実証されていない「通信ゼロ」「完全な匿名化」等は書かない。**

公式: https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/support-info
