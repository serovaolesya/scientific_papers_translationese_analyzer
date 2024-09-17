# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import re

pronouns_analysis = {'я', 'меня', 'мне', 'меня', 'мной', 'мною', 'мне', 'мой', 'моего',
                     'моему', 'моим', 'моем', 'моём', 'моя', 'моей',
                     'мою', 'моею', 'моё', 'мое', 'мои', 'моих', 'моими', 'моих',
                     'ты', 'тебя', 'тебе', 'тобой', 'тобою', 'твой', 'твоего', 'твоему',
                     'твоим', 'твоем', 'твоём', 'твоя', 'твоей', 'твою', 'твоею', 'твое', 'твоё',
                     'твои', 'твоих', 'твоими', 'он', 'его', 'него',
                     'ему', 'нему', 'им', 'ним', 'нем', 'нём', 'она', 'ее', 'её', 'нее', 'неё', 'ей', 'ней',
                     'ею', 'нею', 'оно', 'им', 'ним', 'мы', 'нас', 'нам', 'нами',
                     'наш', 'нашего', 'нашему', 'нашим', 'нашем', 'наша', 'нашей',
                     'нашу', 'нашею', 'наше', 'наши', 'наших', 'наши', 'нашими',
                     'вы', 'вас', 'вам', 'вами', 'ваш', 'вашего', 'вашему',
                     'вашим', 'вашем', 'ваша', 'вашей', 'вашу', 'вашею', 'ваше',
                     'вашего', 'вашему', 'ваше', 'вашим', 'вашем', 'ваши', 'ваших',
                     'вашими', 'они', 'их', 'них', 'ими', 'ними', 'свой', 'своего',
                     'своему', 'своим', 'своем', 'своём', 'своя', 'своей', 'свою', 'своею',
                     'свое', 'своё', 'свои', 'своих', 'своим', 'свои', 'своими', 'себя',
                     'себе', 'собой', 'собою',
                     }

pronouns_analysis_list = list(pronouns_analysis)

pronouns_analysis_list.sort(key=len, reverse=True)

pronouns_set = {
    'аз', 'ваш', 'вашего', 'вашему', 'вашим', 'вашем',
    'ваша', 'вашей', 'вашу', 'вашею', 'ваше',
    'вашего', 'вашему', 'ваше', 'вашим', 'вашем', 'ваши', 'ваших',
    'вашими', 'весь', 'всего', 'всему', 'всего',
    'весь', 'всем', 'всем', 'вся', 'всей', 'всея', 'всей', 'всю', 'всей',
    'всею', 'всей', 'все', 'всего', 'всему', 'все', 'всем', 'всем',
    'все', 'всех', 'всем', 'все', 'всех', 'всеми', 'всех', 'вон', 'вона',
    'вот', 'вот что', 'все', 'всего', 'всему', 'все', 'всем', 'всем', 'все',
    'всех', 'всем', 'все', 'всех', 'всеми', 'всех', 'всяк', 'всякий',
    'всякого', 'всякому', 'всякого', 'всякий', 'всяким', 'всяком', 'всякая',
    'всякой', 'всякой', 'всякую', 'всякою', 'всякой', 'всякой', 'всякое',
    'всякого', 'всякому', 'всякое', 'всяким', 'всяком', 'всякие', 'всяких',
    'всяким', 'всякие', 'всяких', 'всякими', 'всяких', 'всяческий',
    'всяческого', 'всяческому', 'всяческого', 'всяческий', 'всяческим',
    'всяческом', 'всяческая', 'всяческой', 'всяческой', 'всяческую',
    'всяческою', 'всяческой', 'всяческой', 'всяческое', 'всяческого',
    'всяческому', 'всяческое', 'всяческим', 'всяческом', 'всяческие',
    'всяческих', 'всяческим', 'всяческие', 'всяческих', 'всяческими',
    'всяческих', 'вы', 'вас', 'вам', 'вас', 'вами', 'вас', 'где', 'где-либо',
    'где-нибудь', 'где-то', 'докуда', 'докуда-нибудь', 'докуда-то',
    'досель', 'досюда', 'друг друга', 'друг другу', 'друг другом', 'друг друге',
    'друг дружку', 'друг дружке', 'друг дружкой', 'друг дружке', 'другой',
    'другого', 'другому', 'другой', 'другого', 'другим', 'другом', 'другая',
    'другой', 'другой', 'другую', 'другою', 'другой', 'другой', 'другое',
    'другого', 'другому', 'другое', 'другим', 'другом', 'другие', 'других',
    'другим', 'другие', 'других', 'другими', 'других', 'его', 'ее', 'её', 'зачем',
    'зачем-либо', 'зачем-нибудь', 'зачем-то', 'здесь', 'и то и се',
    'и того и сего', 'иже', 'известный', 'иной', 'иного', 'иному', 'иной',
    'иного', 'иным', 'ином', 'иная', 'иной', 'иной', 'иную', 'иною', 'иной',
    'иной', 'иное', 'иного', 'иному', 'иное', 'иным', 'ином', 'иные', 'иных',
    'иным', 'иные', 'иных', 'иными', 'иных', 'их', 'каждый', 'каждого',
    'каждому', 'каждого', 'каждый', 'каждым', 'каждом', 'каждая', 'каждой',
    'каждой', 'каждую', 'каждою', 'каждой', 'каждой', 'каждое', 'каждого',
    'каждому', 'каждое', 'каждым', 'каждом', 'каждые', 'каждых', 'каждым',
    'каждые', 'каждых', 'каждыми', 'каждых', 'как таковой', 'каков', 'какова',
    'каково', 'каковы', 'каковой', 'какового', 'каковому', 'каковой',
    'какового', 'каковым', 'каковом', 'каковая', 'каковой', 'каковой',
    'каковую', 'каковой', 'каковой', 'каковое', 'какового', 'каковому',
    'каковое', 'каковым', 'каковом', 'каковые', 'каковых', 'каковым', 'каковые',
    'каковых', 'каковыми', 'каковых', 'какой', 'какого', 'какому', 'какой',
    'какого', 'каким', 'каком', 'какая', 'какой', 'какой', 'какую', 'какою',
    'какой', 'какой', 'какое', 'какого', 'какому', 'какое', 'каким', 'каком',
    'какие', 'каких', 'каким', 'какие', 'каких', 'какими', 'каких',
    'какой бы то ни было', 'какого бы то ни было', 'какому бы то ни было',
    'какой бы то ни было', 'какого бы то ни было', 'каким бы то ни было',
    'каком бы то ни было', 'какая бы то ни было', 'какой бы то ни было',
    'какой бы то ни было', 'какую бы то ни было', 'какою бы то ни было',
    'какой бы то ни было', 'какой бы то ни было', 'какое бы то ни было',
    'какого бы то ни было', 'какому бы то ни было', 'какое бы то ни было',
    'каким бы то ни было', 'каком бы то ни было', 'какие бы то ни было',
    'каких бы то ни было', 'каким бы то ни было', 'какие бы то ни было',
    'каких бы то ни было', 'какими бы то ни было', 'каких бы то ни было',
    'какой попало', 'какого попало', 'какому попало', 'какой попало',
    'какого попало', 'каким попало', 'каком попало', 'какая попало',
    'какой попало', 'какой попало', 'какую попало', 'какою попало',
    'какой попало', 'какой попало', 'какое попало', 'какого попало',
    'какому попало', 'какое попало', 'каким попало', 'каком попало',
    'какие попало', 'каких попало', 'каким попало', 'какие попало',
    'каких попало', 'какими попало', 'каких попало', 'какой придется',
    'какого придется', 'какому придется', 'какой придется', 'какого придется',
    'каким придется', 'каком придется', 'какая придется', 'какой придется',
    'какой придется', 'какую придется', 'какою придется', 'какой придется',
    'какой придется', 'какое придется', 'какого придется', 'какому придется',
    'какое придется', 'каким придется', 'каком придется', 'какие придется',
    'каких придется', 'каким придется', 'какие придется', 'каких придется',
    'какими придется', 'каких придется', 'какой такой', 'какого такого',
    'какому такому', 'какой такой', 'какого такого', 'каким таким',
    'каком таком', 'какая такая', 'какой такой', 'какой такой', 'какую такую',
    'какою такою', 'какой такой', 'какой такой', 'какое такое',
    'какого такого', 'какому такому', 'какое такое', 'каким таким',
    'каком таком', 'какие такие', 'каких таких', 'каким таким',
    'какие такие', 'каких таких', 'какими такими', 'каких таких',
    'какой там', 'какой там еще', 'какого там еще', 'какому там еще',
    'какой там еще', 'какого там еще', 'каким там еще', 'каком там еще',
    'какая там еще', 'какой там еще', 'какой там еще', 'какую там еще',
    'какою там еще', 'какой там еще', 'какой там еще', 'какое там еще',
    'какого там еще', 'какому там еще', 'какое там еще', 'каким там еще',
    'каком там еще', 'какие там еще', 'каких там еще', 'каким там еще',
    'какие там еще', 'каких там еще', 'какими там еще', 'каких там еще',
    'какой тут', 'какой тут еще', 'какой угодно', 'какой-либо', 'какого-либо',
    'какому-либо', 'какой-либо', 'какого-либо', 'каким-либо', 'каком-либо',
    'какая-либо', 'какой-либо', 'какой-либо', 'какую-либо', 'какой-либо',
    'какой-либо', 'какое-либо', 'какого-либо', 'какому-либо', 'какое-либо',
    'каким-либо', 'каком-либо', 'какие-либо', 'каких-либо', 'каким-либо',
    'какие-либо', 'каких-либо', 'какими-либо', 'каких-либо', 'какой-нибудь',
    'какого-нибудь', 'какому-нибудь', 'какой-нибудь', 'какого-нибудь',
    'каким-нибудь', 'каком-нибудь', 'какая-нибудь', 'какой-нибудь',
    'какой-нибудь', 'какую-нибудь', 'какой-нибудь', 'какой-нибудь',
    'какое-нибудь', 'какого-нибудь', 'какому-нибудь', 'какое-нибудь',
    'каким-нибудь', 'каком-нибудь', 'какие-нибудь', 'каких-нибудь',
    'каким-нибудь', 'какие-нибудь', 'каких-нибудь', 'какими-нибудь',
    'каких-нибудь', 'какой-никакой', 'какой-то', 'какого-то', 'какому-то',
    'какой-то', 'какого-то', 'каким-то', 'каком-то', 'какая-то', 'какой-то',
    'какой-то', 'какую-то', 'какой-то', 'какой-то', 'какое-то', 'какого-то',
    'какому-то', 'какое-то', 'каким-то', 'каком-то', 'какие-то', 'каких-то',
    'каким-то', 'какие-то', 'каких-то', 'какими-то', 'каких-то', 'когда',
    'когда-либо', 'когда-нибудь', 'когда-то', 'кое-где', 'кое-докуда',
    'кое-зачем', 'кое-какой', 'кое-какого', 'кое-какому', 'кое-какой',
    'кое-какого', 'кое-каким', 'кое-каком', 'кое-какая', 'кое-какой',
    'кое-какой', 'кое-какую', 'кое-какой', 'кое-какой', 'кое-какое',
    'кое-какого', 'кое-какому', 'кое-какое', 'кое-каким', 'кое-каком',
    'кое-какие', 'кое-каких', 'кое-каким', 'кое-какие', 'кое-каких',
    'кое-какими', 'кое-каких', 'кое-когда', 'кое-кто', 'кое-кого',
    'кое-кому', 'кое-кого', 'кое-кем', 'кое при ком', 'кое в ком',
    'кое на ком', 'кое о ком', 'кое-ком', 'кое по ком', 'кое-куда',
    'кое-откуда', 'кое-отчего', 'кое-почему', 'кое-чей', 'кое-чьего',
    'кое-чьему', 'кое-чьего', 'кое-чей', 'кое-чьим', 'кое-чьем',
    'кое-чья', 'кое-чьей', 'кое-чьей', 'кое-чью', 'кое-чьей',
    'кое-чьей', 'кое-чье', 'кое-чьего', 'кое-чьему', 'кое-чье',
    'кое-чьим', 'кое-чьем', 'кое-чьи', 'кое-чьих', 'кое-чьим',
    'кое-чьи', 'кое-чьих', 'кое-чьими', 'кое-чьих', 'кое-что',
    'кое-чего', 'кое-чему', 'кое-что', 'кое-чем', 'кое при чем',
    'кое в чем', 'кое на чем', 'кое-чем', 'кое о чем', 'кое по чем',
    'кой', 'коего', 'коему', 'коего', 'кой', 'коим', 'коем', 'коя',
    'коей', 'коей', 'кою', 'коей', 'коей', 'кое', 'коего', 'коему',
    'кое', 'коим', 'коем', 'кои', 'коих', 'коим', 'кои', 'коих',
    'коими', 'коих', 'кой-какой', 'кой-какого', 'кой-какому',
    'кой-какой', 'кой-какого', 'кой-каким', 'кой-каком', 'кой-какая',
    'кой-какой', 'кой-какой', 'кой-какую', 'кой-какою', 'кой-какой',
    'кой-какой', 'кой-какое', 'кой-какого', 'кой-какому', 'кой-какое',
    'кой-каким', 'кой-каком', 'кой-какие', 'кой-каких', 'кой-каким',
    'кой-какие', 'кой-каких', 'кой-какими', 'кой-каких', 'кой-кто',
    'кой-что', 'который', 'которого', 'которому', 'которого', 'который',
    'которым', 'котором', 'которая', 'которой', 'которой', 'которую',
    'которой', 'которой', 'которое', 'которого', 'которому', 'которое',
    'которым', 'котором', 'которые', 'которых', 'которым', 'которые',
    'которых', 'которыми', 'которых', 'который', 'которого', 'которому',
    'которого', 'который', 'которым', 'котором', 'которая', 'которой',
    'которой', 'которую', 'которой', 'которой', 'которое', 'которого',
    'которому', 'которое', 'которым', 'котором', 'которые', 'которых',
    'которым', 'которые', 'которых', 'которыми', 'которых', 'который-либо',
    'которого-либо', 'которому-либо', 'которого-либо', 'который-либо',
    'которым-либо', 'котором-либо', 'которая-либо', 'которой-либо',
    'которой-либо', 'которую-либо', 'которою-либо', 'которой-либо',
    'которой-либо', 'которое-либо', 'которого-либо', 'которому-либо',
    'которое-либо', 'которым-либо', 'котором-либо', 'которые-либо',
    'которых-либо', 'которым-либо', 'которые-либо', 'которых-либо',
    'которыми-либо', 'которых-либо', 'который-нибудь', 'которого-нибудь',
    'которому-нибудь', 'которого-нибудь', 'который-нибудь', 'которым-нибудь',
    'котором-нибудь', 'которая-нибудь', 'которой-нибудь', 'которой-нибудь',
    'которую-нибудь', 'которою-нибудь', 'которой-нибудь', 'которой-нибудь',
    'которое-нибудь', 'которого-нибудь', 'которому-нибудь', 'которое-нибудь',
    'которым-нибудь', 'котором-нибудь', 'которые-нибудь', 'которых-нибудь',
    'которым-нибудь', 'которые-нибудь', 'которых-нибудь', 'которыми-нибудь',
    'которых-нибудь', 'кто', 'кого', 'кому', 'кого', 'кем', 'ком',
    'кто попало', 'кто угодно', 'кто хочешь', 'кто-либо', 'кого-либо',
    'кому-либо', 'кого-либо', 'кем-либо', 'ком-либо', 'кто-нибудь',
    'кого-нибудь', 'кому-нибудь', 'кого-нибудь', 'кем-нибудь', 'ком-нибудь',
    'кто-то', 'кого-то', 'кому-то', 'кого-то', 'кем-то', 'ком-то', 'куда',
    'куда-либо', 'куда-нибудь', 'куда-то', 'любой', 'любого', 'любому',
    'любой', 'любого', 'любым', 'любом', 'любая', 'любой', 'любой', 'любую',
    'любою', 'любой', 'любой', 'любое', 'любого', 'любому', 'любое', 'любым',
    'любом', 'любые', 'любых', 'любым', 'любые', 'любых', 'любыми', 'любых',
    'мало какой', 'мало кто', 'мало что', 'мой', 'моего', 'моему', 'моего',
    'мой', 'моим', 'моем', 'моя', 'моей', 'моей', 'мою', 'моею', 'моей',
    'моей', 'мое', 'моё', 'моего', 'моему', 'мое', 'моим', 'моем', 'моём', 'мои', 'моих',
    'моим', 'мои', 'моих', 'моими', 'моих', 'мы', 'нас', 'нам', 'нас', 'нами',
    'нас', 'на то на се', 'наш', 'нашего', 'нашему', 'нашего', 'наш', 'нашим',
    'нашем', 'наша', 'нашей', 'нашей', 'нашу', 'нашею', 'нашей', 'нашей',
    'наше', 'нашего', 'нашему', 'наше', 'нашим', 'нашем', 'наши', 'наших',
    'нашим', 'наши', 'наших', 'нашими', 'наших', 'некий', 'некоего',
    'некоему', 'некоего', 'некий', 'неким', 'некоим', 'некоем', 'неком',
    'некая', 'некоей', 'некой', 'некоей', 'некой', 'некую', 'некой',
    'некоей', 'некой', 'некоей', 'некое', 'некоего', 'некоему', 'некое',
    'неким', 'неком', 'некие', 'неких', 'неким', 'некие', 'неких', 'некими',
    'неких', 'некогда', 'некоторый', 'некоторого', 'некоторому', 'некоторого',
    'некоторый', 'некоторым', 'некотором', 'некоторая', 'некоторой',
    'некоторой', 'некоторую', 'некоторой', 'некоторой', 'некоторое',
    'некоторого', 'некоторому', 'некоторое', 'некоторым', 'некотором',
    'некоторые', 'некоторых', 'некоторым', 'некоторые', 'некоторых',
    'некоторыми', 'некоторых', 'некто', 'несколько', 'нескольких',
    'нескольким', 'нескольких', 'несколько', 'несколькими', 'нескольких',
    'нет кто', 'некого', 'некому', 'некого', 'некем', 'не ком', 'нет что',
    'нечего', 'нечему', 'нечего', 'нечем', 'не чем', 'нечто', 'нечто вроде',
    'ни про то ни про се', 'ни то ни се', 'ни шиша', 'нигде', 'нидокуда',
    'низачем', 'никак', 'никаков', 'никакова', 'никаково', 'никаковы',
    'никакой', 'никакого', 'никакому', 'никакой', 'никакого', 'никаким',
    'ни в каком', 'ни на каком', 'ни о каком', 'ни по каком', 'ни при каком',
    'никакая', 'ни какой', 'никакой', 'никакой', 'никакую', 'никакой',
    'никакое', 'ни каком', 'никакого', 'никакому', 'никакое', 'никаким',
    'никакие', 'ни каких', 'никаких', 'никаким', 'никакие', 'никаких',
    'никакими', 'никогда', 'никой', 'никоего', 'никоему', 'никоего', 'никой',
    'никоим', 'никоем', 'никои', 'никоих', 'никоим', 'никои', 'никоих',
    'никоими', 'никоих', 'никоторый', 'никоторого', 'никоторому', 'никоторого',
    'никоторый', 'никоторым', 'никотором', 'никоторая', 'никоторой',
    'никоторой', 'никоторую', 'никоторою', 'никоторой', 'никоторой',
    'никоторое', 'никоторого', 'никоторому', 'никоторое', 'никоторым',
    'никотором', 'никоторые', 'никоторых', 'никоторым', 'никоторые',
    'никоторых', 'никоторыми', 'никоторых', 'никто', 'никого', 'никому',
    'никого', 'никем', 'ни ком', 'никтошеньки', 'никогошеньки',
    'никомушеньки', 'никогошеньки', 'никуда', 'ниоткуда', 'ниотчего',
    'нипочем', 'нипочему', 'ничегохоньки', 'ничегохонько', 'ничегошеньки',
    'ничегошенько', 'ничей', 'ничьего', 'ничьему', 'ничей', 'ничьего',
    'ничей', 'ничьим', 'ничьем', 'ничья', 'ничьей', 'ничьей', 'ничью',
    'ничьей', 'ничьей', 'ничье', 'ничьего', 'ничьему', 'ничье', 'ничьим',
    'ничьем', 'ничьи', 'ничьих', 'ничьим', 'ничьи', 'ничьих', 'ничьими',
    'ничьих', 'ничто', 'ничего', 'ничему', 'ничто', 'ничем', 'ни чем',
    'ничто', 'нечего', 'нечему', 'нечего', 'нечем', 'не чем', 'о том о сем',
    'один', 'одного', 'одному', 'одного', 'один', 'одним', 'одном', 'одна',
    'одной', 'одной', 'одну', 'одною', 'одной', 'одной', 'одно', 'одного',
    'одному', 'одно', 'одним', 'одном', 'одни', 'одних', 'одним', 'одни',
    'одних', 'одними', 'одних', 'один и тот же', 'одного и того же',
    'одному и тому же', 'одного и того же', 'один и тот же', 'одним и тем же',
    'одном и том же', 'одна и та же', 'одной и той же', 'одной и той же',
    'одну и ту же', 'одной и той же', 'одной и той же', 'одно и то же',
    'одного и того же', 'одному и тому же', 'одного и того же',
    'одно и то же', 'одним и тем же', 'одном и том же', 'одни и те же',
    'одних и тех же', 'одним и тем же', 'одни и те же', 'одних и тех же',
    'одними и теми же', 'одних и тех же', 'он', 'его', 'него', 'ему', 'нему',
    'им', 'ним', 'нем', 'нём', 'она', 'ее', 'её', 'нее', 'неё', 'ей', 'ней',
    'ею', 'нею', 'оно', 'его', 'него', 'ему',
    'нему', 'им', 'ним', 'нем', 'они', 'их', 'них', 'ним',
    'им', 'ими', 'ними', 'оное', 'оного', 'оному', 'оное',
    'оным', 'оном', 'оный', 'оного', 'оному', 'оного', 'оный', 'оным', 'оном',
    'оная', 'оной', 'оной', 'оную', 'оною', 'оной', 'оной', 'оное', 'оного',
    'оному', 'оное', 'оным', 'оном', 'оные', 'оных', 'оным', 'оные', 'оных',
    'оными', 'оных', 'оный', 'оного', 'оному', 'оного', 'оный', 'оным',
    'оном', 'оная', 'оной', 'оной', 'оную', 'оною', 'оной', 'оной', 'оное',
    'оного', 'оному', 'оное', 'оным', 'оном', 'оные', 'оных', 'оным', 'оные',
    'оных', 'оными', 'оных', 'откуда', 'откуда-либо', 'откуда-нибудь',
    'откуда-то', 'отсель', 'отсюда', 'отсюдова', 'оттуда', 'оттудова',
    'отчего', 'отчего-либо', 'отчего-нибудь', 'отчего-то', 'подобного рода',
    'потому', 'почему', 'почему-либо', 'почему-нибудь', 'почему-то',
    'разного рода', 'сам', 'самого', 'самому', 'самого', 'сам', 'самим',
    'самом', 'сама', 'самой', 'самой', 'самое', 'саму', 'самою', 'самой',
    'самой', 'само', 'самого', 'самому', 'само', 'самим', 'самом', 'сами',
    'самих', 'самим', 'сами', 'самих', 'самими', 'самих', 'самый', 'самого',
    'самому', 'самого', 'самый', 'самым', 'самом', 'самая', 'самой', 'самой',
    'самую', 'самою', 'самой', 'самой', 'самое', 'самого', 'самому', 'самое',
    'самым', 'самом', 'самые', 'самых', 'самым', 'самые', 'самых', 'самыми',
    'самых', 'своего рода', 'свой', 'своего', 'своему', 'своего', 'свой',
    'своим', 'своем', 'своём', 'своя', 'своей', 'своей', 'свою', 'своею', 'своей',
    'своей', 'свое', 'своего', 'своему', 'свое', 'своё', 'своим', 'своем', 'свои',
    'своих', 'своим', 'свои', 'своих', 'своими', 'своих', 'себя', 'себе',
    'себя', 'собой', 'собою', 'себе', 'сей', 'сего', 'сему', 'сей', 'сего',
    'сим', 'сем', 'сия', 'сией', 'сией', 'сию', 'сю', 'сией', 'сиею', 'сией',
    'сие', 'сего', 'сему', 'сие', 'сим', 'сем', 'сии', 'сих', 'сим', 'сии',
    'сих', 'сими', 'сих', 'сий', 'сего', 'сему', 'сего', 'сий', 'сим', 'сим',
    'сколькие', 'сколько', 'скольких', 'скольким', 'скольких', 'сколько',
    'сколькими', 'скольких', 'сколько-нибудь', 'скольких-нибудь',
    'скольким-нибудь', 'скольких-нибудь', 'сколько-нибудь',
    'сколькими-нибудь', 'скольких-нибудь', 'сколько-то', 'скольких-то',
    'скольким-то', 'скольких-то', 'сколько-то', 'сколькими-то', 'скольких-то',
    'столько', 'стольких', 'стольким', 'стольких', 'столько', 'столькими',
    'стольких', 'сюда', 'так', 'таковой', 'такового', 'таковому', 'таковой',
    'такового', 'таковым', 'таковом', 'таков', 'такова', 'таковая',
    'таковой', 'таковой', 'таковую', 'таковою', 'таковой', 'таковой',
    'таково', 'таковое', 'такового', 'таковому', 'таковое', 'таковым',
    'таковом', 'таковы', 'таковые', 'таковых', 'таковым', 'таковые',
    'таковых', 'таковыми', 'таковых', 'таковский', 'таковского', 'таковскому',
    'таковского', 'таковский', 'таковским', 'таковском', 'таковская',
    'таковской', 'таковской', 'таковскую', 'таковскою', 'таковской',
    'таковской', 'таковское', 'таковского', 'таковскому', 'таковское',
    'таковского', 'таковским', 'таковском', 'таковские', 'таковских',
    'таковским', 'таковские', 'таковских', 'таковскими', 'таковских',
    'такого рода', 'такой', 'такого', 'такому', 'такой', 'такого', 'таким',
    'таком', 'такая', 'такой', 'такой', 'такую', 'такою', 'такой', 'такой',
    'такое', 'такого', 'такому', 'такое', 'таким', 'таком', 'такие', 'таких',
    'таким', 'такие', 'таких', 'такими', 'таких', 'такой-сякой', 'такой-то',
    'там', 'твой', 'твоего', 'твоему', 'твоего', 'твой', 'твоим', 'твоем',
    'твоя', 'твоей', 'твоей', 'твою', 'твоею', 'твоей', 'твоей', 'твое', 'твоё',
    'твоего', 'твоему', 'твое', 'твоим', 'твоем', 'твоём', 'твои', 'твоих', 'твоим',
    'твои', 'твоих', 'твоими', 'твоих', 'то', 'того', 'тому', 'то', 'тем',
    'том', 'то да се', 'то же самое', 'тогда', 'тот', 'того', 'тому', 'того',
    'тем', 'том', 'та', 'той', 'той', 'ту', 'тою', 'той', 'той', 'те', 'тех',
    'тем', 'тех', 'теми', 'тех', 'тот', 'того', 'тому', 'того', 'тот', 'тем',
    'том', 'та', 'той', 'той', 'ту', 'тою', 'той', 'той', 'то', 'того',
    'тому', 'то', 'тем', 'том', 'те', 'тех', 'тем', 'те', 'тех', 'теми',
    'тех', 'тот или другой', 'тот или иной', 'туда', 'туда-сюда', 'тут', 'ты',
    'тебя', 'тебе', 'тебя', 'тобой', 'тобою', 'тебе', 'указанный',
    'указанного', 'указанному', 'указанного', 'указанный', 'указанным',
    'указанном', 'указанная', 'указанной', 'указанной', 'указанную',
    'указанною', 'указанной', 'указанной', 'указанное', 'указанного',
    'указанному', 'указанное', 'указанным', 'указанном', 'указанные',
    'указанных', 'указанным', 'указанные', 'указанных', 'указанными',
    'указанных', 'хоть какой', 'чаво', 'чей', 'чьего', 'чьему', 'чьего',
    'чей', 'чьим', 'чьем', 'чья', 'чьей', 'чьей', 'чью', 'чьей', 'чьей',
    'чье', 'чьего', 'чьему', 'чье', 'чьим', 'чьем', 'чьи', 'чьих', 'чьим',
    'чьи', 'чьих', 'чьими', 'чьих', 'чей бы ни', 'чей-либо', 'чьего-либо',
    'чьему-либо', 'чей-либо', 'чьим-либо', 'чьем-либо', 'чья-либо',
    'чьей-либо', 'чьей-либо', 'чью-либо', 'чьей-либо', 'чьей-либо',
    'чье-либо', 'чьего-либо', 'чьему-либо', 'чье-либо', 'чьим-либо',
    'чьем-либо', 'чьи-либо', 'чьих-либо', 'чьим-либо', 'чьи-либо',
    'чьих-либо', 'чьими-либо', 'чьих-либо', 'чей-нибудь', 'чьего-нибудь',
    'чьему-нибудь', 'чьего-нибудь', 'чей-нибудь', 'чьим-нибудь',
    'чьем-нибудь', 'чья-нибудь', 'чьей-нибудь', 'чьей-нибудь', 'чью-нибудь',
    'чьей-нибудь', 'чьей-нибудь', 'чье-нибудь', 'чьего-нибудь',
    'чьему-нибудь', 'чье-нибудь', 'чьим-нибудь', 'чьем-нибудь', 'чьи-нибудь',
    'чьих-нибудь', 'чьим-нибудь', 'чьи-нибудь', 'чьих-нибудь', 'чьими-нибудь',
    'чьих-нибудь', 'чей-то', 'чьего-то', 'чьему-то', 'чьего-то', 'чей-то',
    'чьим-то', 'чьем-то', 'чья-то', 'чьей-то', 'чьей-то', 'чью-то',
    'чьей-то', 'чьей-то', 'чье-то', 'чьего-то', 'чьему-то', 'чье-то',
    'чьим-то', 'чьем-то', 'чьи-то', 'чьих-то', 'чьим-то', 'чьи-то', 'чьих-то',
    'чьими-то', 'чьих-то', 'что', 'чем', 'чему', 'что', 'чем', 'чего',
    'что попало', 'что угодно', 'что хочешь', 'что-либо', 'чего-либо',
    'чему-либо', 'что-либо', 'чем-либо', 'чем-либо', 'что-нибудь',
    'чего-нибудь', 'чему-нибудь', 'что-нибудь', 'чем-нибудь', 'чем-нибудь',
    'что-нибудь вроде', 'что-то', 'чего-то', 'чему-то', 'что-то', 'чем-то',
    'чем-то', 'что-то вроде', 'эдак', 'эдакий', 'эдакого', 'эдакому',
    'эдакого', 'эдакий', 'эдаким', 'эдаком', 'эдакая', 'эдакой', 'эдакой',
    'эдакую', 'эдакою', 'эдакой', 'эдакой', 'эдакое', 'эдакого', 'эдакому',
    'эдакое', 'эдаким', 'эдаком', 'эдакие', 'эдаких', 'эдаким', 'эдакие',
    'эдаких', 'эдакими', 'эдаких', 'экий', 'экого', 'экому', 'экого', 'экий',
    'эким', 'эком', 'эка', 'экая', 'экой', 'экой', 'экую', 'экою', 'экой',
    'экой', 'эко', 'экое', 'экого', 'экому', 'экое', 'эким', 'эком', 'эки',
    'экие', 'эких', 'эким', 'экие', 'эких', 'экими', 'эких', 'этак', 'этакий',
    'этакого', 'этакому', 'этакого', 'этакий', 'этаким', 'этаком', 'этакая',
    'этакой', 'этакой', 'этакую', 'этакою', 'этакой', 'этакой', 'этакое',
    'этакого', 'этакому', 'этакое', 'этаким', 'этаком', 'этакие', 'этаких',
    'этаким', 'этакие', 'этаких', 'этакими', 'этаких', 'это', 'этого',
    'этому', 'это', 'этим', 'этом', 'этот', 'этого', 'этому', 'этого', 'этот',
    'этим', 'этом', 'эта', 'этой', 'этой', 'эту', 'этою', 'этой', 'этой',
    'это', 'этого', 'этому', 'это', 'этим', 'этом', 'эти', 'этих', 'этим',
    'эти', 'этих', 'этими', 'этих', 'я', 'меня', 'мне', 'меня', 'мной',
    'мною', 'мне'}

pronouns_list = list(pronouns_set)

pronouns_list.sort(key=len, reverse=True)

pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, pronouns_list)) + r')\b')

text = """"
Теперь программа должна учитывать отметим, что слова после союза в правом окружении. Пожалуйста, проверьте, соответствует ли это вашим ожиданиям.
"""

if __name__ == "__main__":
    lowercase_text = text.lower()

    found_pronouns = [m.group() for m in pattern.finditer(lowercase_text)]

    print(found_pronouns)
    print(len(found_pronouns))