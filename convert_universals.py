import ms




universal = ms.loadCSV(r"tables\universal_metabolites.csv")
universal.renameColumns(RT_max="rtmax", RT_min="rtmin", M0="m0", link_to_pubchem="url", compouind_name="name")
universal.replaceColumn("rtmax", universal.rtmax * 60)
universal.replaceColumn("rtmin", universal.rtmin * 60)

universal.set(universal.colFormats, "rtmin", '"%.2fm" % (o/60.0)')
universal.set(universal.colFormats, "rtmax", '"%.2fm" % (o/60.0)')

universal._print()
universal.store(r"tables\universal_metabolites.table", True)

