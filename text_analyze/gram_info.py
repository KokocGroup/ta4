# -*-coding: utf-8 -*-


class GramInfo(object):
    __slots__ = ('infinitive', 'lemma', 'speech', 'info')

    def __init__(self, gi):
        u"""
        :type  gi: :py:class:`dict`
        :param gi: словарь с грамматической информацией из *pymorphy*
        """

        self.infinitive = gi.get('norm', "")
        self.lemma = gi.get('lemma', "")
        self.speech = gi.get('class', "")
        self.info = []
        info = gi.get('info')
        if info:
            if isinstance(info, (str, unicode)):
                info = info.split(',')
            self.info = [i.strip().encode('utf-8') for i in info]

    def __repr__(self):
        return u"<inf: {}; lemma: {}; speech: {}; info: {}>".format(
            self.infinitive,
            self.lemma,
            self.speech,
            ",".join(self.info)
        )
