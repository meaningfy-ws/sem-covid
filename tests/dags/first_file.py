def download_documents_and_enrich_json(self, *args, **context):
    self.assert_filename(**context)

    json_file_name = context['dag_run'].conf['filename']
    logger.info(f'Enriched fragments will be saved locally to the bucket {config.EU_CELLAR_BUCKET_NAME}')
    logger.info(f'Processing {json_file_name}')

    minio = self.store_registry.minio_object_store(config.EU_CELLAR_BUCKET_NAME)

    json_content = json.loads(minio.get_object(json_file_name).decode('utf-8'))

    counter = {
        'html': 0,
        'pdf': 0
    }

    json_content[CONTENT_PATH_KEY] = list()
    if json_content.get('manifs_html'):
        for html_manifestation in json_content.get('htmls_to_download'):
            filename = hashlib.sha256(html_manifestation.encode('utf-8')).hexdigest()

            logger.info(f"Downloading HTML manifestation for {(json_content['title'] or json_content['work'])}")

            html_file = filename + '_html.zip'
            if self.download_file(json_content, html_manifestation, html_file, minio):
                counter['html'] += 1
    elif json_content.get('manifs_pdf'):
        for pdf_manifestation in json_content.get('pdfs_to_download'):

            filename = hashlib.sha256(pdf_manifestation.encode('utf-8')).hexdigest()

            logger.info(f"Downloading PDF manifestation for {(json_content['title'] or json_content['work'])}")

            pdf_file = filename + '_pdf.zip'
            if self.download_file(json_content, pdf_manifestation, pdf_file, minio):
                counter['pdf'] += 1
    else:
        logger.warning(f"No manifestation has been found for {json_content['work']}")

    minio.put_object(json_file_name, json.dumps(json_content))

    logger.info(f"Downloaded {counter['html']} HTML manifestations and {counter['pdf']} PDF manifestations.")