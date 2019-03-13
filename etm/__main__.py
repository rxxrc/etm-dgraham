#! ./env/bin/python
def main():
    import logging
    import logging.config
    logger = logging.getLogger()

    import sys
    MIN_PYTHON = (3, 6)
    if sys.version_info < MIN_PYTHON:
        sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)
    import os
    # lib_path = os.path.relpath('')
    # sys.path.append(lib_path)

    import etm.__version__ as version
    etm_version = version.version
    etmdir = os.getcwd()
    # homedir = os.path.expanduser("~")
    # etmdir = os.path.normpath(os.path.join(homedir, "etm"))


    loglevel = 2 # info
    log_levels = [str(x) for x in range(1, 6)]
    if len(sys.argv) > 1 and sys.argv[1] in log_levels:
        loglevel = sys.argv.pop(1)
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        etmdir = sys.argv.pop(1)

    logdir = os.path.normpath(os.path.join(etmdir, 'logs'))
    if not os.path.isdir(logdir):
        os.makedirs(logdir)

    backdir = os.path.normpath(os.path.join(etmdir, 'backups'))
    if not os.path.isdir(backdir):
        os.makedirs(backdir)

    import etm.options as options
    settings = options.Settings(etmdir).settings
    setup_logging = options.setup_logging
    setup_logging(loglevel, logdir)


    import pendulum
    locale = settings.get('locale', None)
    if locale:
        pendulum.set_locale(locale)
    today = pendulum.today()
    day = today.end_of('week')  # Sunday
    WA = {i: day.add(days=i).format('ddd')[:2] for i in range(1, 8)}

    import etm.data as data
    dbfile = os.path.normpath(os.path.join(etmdir, 'db.json'))
    ETMDB = data.initialize_tinydb(dbfile)
    DBITEM = ETMDB.table('items', cache_size=None)
    DBARCH = ETMDB.table('archive', cache_size=None)

    from etm.model import about
    import etm.model as model
    model.etm_version = etm_version
    model.logger = logger
    model.WA = WA
    model.ETMDB = ETMDB
    model.DBITEM = DBITEM
    model.DBARCH = DBARCH
    model.settings = settings
    # we put settings into the model namespace so model.Dataview will have it
    dataview = model.DataView(etmdir)
    item = model.Item(etmdir)
    format_time = model.format_time
    format_datetime = model.format_datetime
    format_duration = model.format_duration
    # since dataview calls schedule it will also have settings
    completions = dataview.completions
    expansions = settings["expansions"]
    if expansions:
        for x in expansions:
            completions.append(f"@x {x}")
    style = dataview.settings["style"]
    parse_datetime = model.parse_datetime

    logger.info(f"model.logger: {model.logger}")
    logger.info(f"initialized TinyDB using {dbfile}")


    import etm.view as view
    view.logger = logger
    view.model = model
    view.about = about
    view.wrap = model.wrap
    view.settings = settings
    view.format_time = format_time
    view.format_datetime = format_datetime
    view.format_duration = format_duration
    view.parse_datetime = parse_datetime
    view.ETMDB = ETMDB
    view.DBITEM = DBITEM
    view.DBARCH = DBARCH

    # view.ampm = settings['ampm']
    view.dataview = dataview
    view.item = item
    view.completions = completions
    view.expansions = expansions
    view.terminal_style = style
    logger.info(f"setting terminal_style: {style}")

    # main(etmdir)

    if len(sys.argv) > 1:
        if sys.argv[1] == 'doctest':
            logger.info(f"calling data.do_doctest with etmdir: {etmdir}, argv: {sys.argv}")
            from model import do_doctest
            do_doctest()
        else:
            logger.info(f"calling data.main with etmdir: {etmdir}, argv: {sys.argv}")
            from etm.model import main
            main(etmdir, sys.argv)
            # sys.exit()

    else:
        logger.info(f"calling view.main with etmdir: {etmdir}")
        from etm.view import main
        main(etmdir)


if __name__ == "__main__":
    main()

