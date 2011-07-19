from Polarity cimport *


class _Polarity:

    POSNULL = 0
    POSITIVE = 1
    NEGATIVE = 2


    def __init__(self, enumcode):

        self.enumcode = enumcode
        # workaround. access to enums inside classes makes some trouble...
        self.polarityAsString  =  { _Polarity.POSNULL: "POSNULL", \
                                    _Polarity.POSITIVE: "POSITIVE", \
                                    _Polarity.NEGATIVE: "NEGATIVE", \
                                    # 3: "SIZE_OF_POLARITY", \
                                  }[enumcode]


    def __str__(self):
        return self.polarityAsString
