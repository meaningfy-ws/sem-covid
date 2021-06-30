def download_documents_and_enrich_json_callable(**context):
    if "work" not in context['dag_run'].conf:
        logger.error(
            "Could not find the work in the provided configuration. This DAG is to be triggered by its parent only.")
        return

    work = context['dag_run'].conf['work']
    logger.info(f'Enriched fragments will be saved locally to the bucket {config.EU_FINREG_CELLAR_BUCKET_NAME}')

    minio = StoreRegistry.minio_object_store(config.EU_FINREG_CELLAR_BUCKET_NAME)
    json_filename = FIELD_DATA_PREFIX + hashlib.sha256(work.encode('utf-8')).hexdigest() + ".json"
    json_content = get_single_item(QUERY.replace("%WORK_ID%", work), json_filename)

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
            if download_file(json_content, html_manifestation, html_file, minio):
                counter['html'] += 1
    elif json_content.get('manifs_pdf'):
        for pdf_manifestation in json_content.get('pdfs_to_download'):

            filename = hashlib.sha256(pdf_manifestation.encode('utf-8')).hexdigest()

            logger.info(f"Downloading PDF manifestation for {(json_content['title'] or json_content['work'])}")

            pdf_file = filename + '_pdf.zip'
            if download_file(json_content, pdf_manifestation, pdf_file, minio):
                counter['pdf'] += 1
    else:
        logger.warning(f"No manifestation has been found for {(json_content['title'] or json_content['work'])}")

    minio.put_object(json_filename, json.dumps(json_content))

    logger.info(f"Downloaded {counter['html']} HTML manifestations and {counter['pdf']} PDF manifestations.")