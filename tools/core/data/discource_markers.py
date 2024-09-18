# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import re

# Global connection
topic_intro_dm = {'речь пойдет о', 'будет рассмотрено',
                  'будет затронут вопрос о', 'мы рассмотрим',
                  'статья посвящена', 'основное внимание уделено',
                  'требует своего объяснения', 'требуют своего объяснения',
                  'требует объяснения', 'требуют объяснения',
                  'цель данной статьи', 'цель данной работы',
                  'в статье приведены', 'целью работы',
                  'нуждается в пояснении', 'нуждаются в пояснении',
                  'требует разъяснения', 'требуют разъяснения'}

info_sequence = {'во-первых', 'во-вторых', 'в-третьих', 'в-четвертых',
                 'сначала', 'прежде всего', 'наконец', 'сперва рассмотрим',
                 'вначале рассмотрим', 'рассмотрим сначала', 'начнем с',
                 'первым делом', 'в первую очередь', 'в завершение',
                 'в заключение', 'в конце концов', 'начиная с того что',
                 'начиная с того, что', 'начнем с того что',
                 'начнем с того, что', }

illustration_dm = {'рис.', 'табл.', 'прил.', 'раздел', 'в таблице видно',
                   'из таблицы видно', 'на диаграмме', 'на рисунке',
                   'данные представлены', 'в таблице приведены примеры',
                   'на рисунке представлен график', 'представлены в',
                   'представлена в', 'представлен в', 'как видно из'}

material_sequence = {'как говорилось выше', 'как уже отмечалось',
                     'как отмечалось ранее', 'как было показано ранее',
                     'о чем будет сказано', 'об этом будет сказано',
                     'о чем речь пойдет', 'об этом речь пойдет',
                     'ниже мы рассмотрим', 'ниже будет рассмотрено',
                     'далее мы рассмотрим', 'далее будет рассмотрено'}

conclusion_dm = {'поэтому', 'исходя из ', 'исходя из того что', 'исходя из того, что',
                 'таким образом', 'в результате того, что', 'в результате чего',
                 'следовательно', 'в результате', 'итак', 'в конечном итоге',
                 'согласно этому', 'в целом', 'в связи с тем', ', так что',
                 'в связи с этим', 'в связи с чем', 'отсюда', 'вследствие чего',
                 'значит,', 'в заключение', 'в конце', 'в довершение', 'в силу чего', 'из-за чего',
                 'подводя итог', 'подводя итоги', 'в итоге', 'следует вывод',
                 'можно сделать вывод', 'напрашивается вывод', 'вследствие',
                 'вследствие того что', 'вследствие того, что', 'причину следует искать', 'приходится заключить',
                 'в конечном счёте', 'в конечном счете', 'т.о.,', 'подводя итог', 'на основании этого',
                 'на основании чего', 'отчего', 'потому', }

# Local connection
intro_new_addit_info = {'причем', 'причём', 'к тому ж', 'к тому же', 'в частности', 'а именно',
                        'вместе с тем', 'в том числе', 'кроме того', 'кроме как', 'кроме того что',
                        'кроме того, что', 'кроме',
                        'более того', 'помимо того', 'вдобавок', 'к слову',
                        'попутно скажем', 'кстати говоря', 'с другой стороны',
                        'в то же время', 'в то время как', 'в т.ч.', 'в т. ч.',
                        'включая', 'а так же', 'в том числе', 'в том числе и', 'да еще',
                        'да еще и', 'да и', 'да и то', 'так же', 'так же как',
                        'так же как и', ', так и', 'тем более что',  'не только','а также',}

info_explanation_or_repetition = {'то есть', 'т. е.', 'другими словами', 'из-за', 'из-за того что', 'из-за того, что',
                                  'иначе говоря', 'точнее сказать', 'в том смысле, что',
                                  'точнее говоря', 'проще говоря', 'т.е', 'на том основании что',
                                  'на том основании, что', 'на том основании', 'потому как',
                                  'потому что', 'потому, что', 'ради того чтоб', 'ради того чтобы',
                                  'ради того, чтоб', 'ради того, чтобы', 'чтоб', 'чтобы',
                                  'так сказать', 'поскольку', 'ввиду того что', 'ввиду того, что',
                                  'иными словами', 'в связи с тем, что', 'в связи с тем что',
                                  'в связи с чем', 'в силу того, что', 'в силу того что',
                                  'для того чтоб', 'для того чтобы', 'для того, чтоб',
                                  'для того, чтобы', 'за счет того что', 'затем что', 'затем, что',
                                  'затем чтоб', 'затем чтобы', 'затем, чтоб', 'затем, чтобы', 'по поводу того что',
                                  'по поводу того, что', 'по причине того, что', 'по причине того что',
                                  'по случаю того что', 'по случаю того, что', 'по той причине что',
                                  'по той причине, что', 'по тому поводу, что', 'по тому поводу что',
                                  'под предлогом того, что', 'под предлогом, что', 'под тем предлогом, что',
                                  'при всем том', 'при всем том, что', 'при том что',
                                  'притом', 'причем', 'промеж тем', 'с таким расчетом, чтоб', 'с таким расчетом, чтобы',
                                  'с тем расчетом, чтоб', 'с тем расчетом, чтобы', 'с тем чтоб',
                                  'с тем чтобы', 'с тем, чтоб', 'с тем, чтобы', 'с той целью, чтоб',
                                  'с той целью, чтобы', 'с целью, чтоб', 'с целью, чтобы', 'так как', 'т.к.', 'т. к.',
                                  }

contrast_dm = {'а', 'а ведь', 'но', 'однако', 'хотя', 'тем не менее', 'впрочем', 'наоборот',
               'вместе с тем', 'между тем', 'меж тем, как', 'между тем как', 'при этом', 'в отличие от',
               'в противном случае', 'невзирая на то что', 'невзирая на то, что',
               'с одной стороны,', 'с другой стороны,', 'за исключением', 'за исключением',
               'за исключением того что', 'за исключением того, что', 'впрочем',
               'правда,', 'а на самом деле', 'несмотря на', 'в то время как', 'зато',
               'напротив,', 'на деле же', 'вопреки', 'вопреки тому что', 'вопреки тому, что', }

examples_introduction_dm = {'пример', 'например', 'к примеру', 'на примере',
                            'для иллюстрации', 'такие как', 'такой как,',
                            'такая как', 'такого как', 'таким как', 'такими как',
                            'таких как', 'такой как', 'такому как', 'таком как',
                            'такую как', 'такое как', 'ради примера', 'так,',
                            'в частности', 'взять хотя бы', 'скажем',
                            'а именно', 'наподобие', 'приводим примеры', }

# ДМ для репрезентации авторского начала в научном тексте.
author_opinion = {'на наш взгляд', 'по нашему мнению', 'с нашей точки зрения',
                  'как нам кажется', 'мы уверены', 'думается'}

categorical_attitude_dm = {'конечно,', 'разумеется,', 'несомненно',
                           'безусловно', 'действительно', 'на самом деле',
                           'наверняка', 'очевидно', 'не вызывает сомнения',
                           'бесспорно', 'справедливо', 'как правило',
                           'к сожалению', 'естественно,', 'ясно',
                           'необычно', 'наиболее интересно', 'неудивительно',
                           'примечательно', 'показательно', 'убедительно',
                           'без сомнения', }

less_categorical_attitude_dm = {'возможно', 'вероятно', 'наверно', 'наверное',
                                'по-видимому', 'допустим', 'можно полагать',
                                'можно предположить', 'можно допустить',
                                'сомнительно', 'едва ли', 'вроде бы',
                                'скорее всего', 'маловероятно', 'вряд ли',
                                'кажется', 'похоже'}

# ДМ, регулирующие процесс взаимодействия автора и читателя
call_to_action_dm = {'см.', 'смотри', 'ср.', 'сравни'}

joint_action = {'рассмотрим', 'обозначим', 'перейдем к', 'обсудим', 'предположим'}

putting_emphasis_dm = {'следует отметить', ' необходимо отметить',
                       'важно отметить', 'уместно отметить',
                       'важным представляется отметить',
                       'необходимым представляется отметить',
                       'следует подчеркнуть', ' необходимо подчеркнуть',
                       'важно подчеркнуть', 'уместно подчеркнуть',
                       'важным представляется подчеркнуть',
                       'необходимым представляется подчеркнуть',
                       'отметим, что', 'подчеркнем, что',
                       'стоит упомянуть', 'важно уточнить',
                       'необходимо уточнить', 'обратим внимание на',
                       'важно обратить внимание на то, что', 'между прочим',
                       'примечательно, что'}

refer_to_background_knowledge = {'не секрет, что', 'общеизвестно',
                                 'как известно', 'принято считать',
                                 'известно, что'}

hybrid_words = {'в основном', 'во многом', 'без малого',
                'в идеале', 'не без основания', 'в сущности', 'по существу',
                'по сути', 'в большинстве своем', 'не без основания',
                'возникает вопрос', 'встает вопрос', 'в подтверждение того, что'}

all_sci_dm = topic_intro_dm | info_sequence | illustration_dm | \
             material_sequence | conclusion_dm | intro_new_addit_info | \
             info_explanation_or_repetition | contrast_dm | \
             examples_introduction_dm | author_opinion | categorical_attitude_dm | \
             less_categorical_attitude_dm | call_to_action_dm | joint_action | \
             putting_emphasis_dm | refer_to_background_knowledge

final_sci_dm_list = list(all_sci_dm)
final_sci_dm_list.sort(key=len, reverse=True)
pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, final_sci_dm_list)) + r')\b')

text = """"
...
"""

if __name__ == "__main__":
    lowercase_text = text.lower()

    found_sci_dms = [m.group() for m in pattern.finditer(lowercase_text)]

    print(found_sci_dms)
    print(len(found_sci_dms))