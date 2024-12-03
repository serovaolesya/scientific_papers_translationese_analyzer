# -*- coding: utf-8 -*-
import json
from collections import defaultdict

import re
import sqlite3 as sq

from colorama import Fore, Style, init
from rich.table import Table
from rich.console import Console

from tools.core.constants import NON_TRANSLATED_DB_NAME, HUMAN_TRANSLATED_DB_NAME, MACHINE_TRANSLATED_DB_NAME, \
    AUTH_CORPUS_NAME, HT_CORPUS_NAME, MT_CORPUS_NAME
from tools.interference.contextual_func_words import print_trigram_tables_with_func_w
from tools.miscellaneous.flesh_readability_score import display_readability_index
from tools.miscellaneous.func_words_freqs import print_func_w__frequencies
from tools.interference.n_grams_analyzer import display_ngrams_summary
from tools.explicitation.named_entities_extraction import display_entities
from tools.miscellaneous.passive_to_all_verbs_ratio import print_passive_verbs_ratio
from tools.normalisation.pmi import calculate_pmi, display_pmi_table
from tools.interference.positional_token_freq import print_frequencies
from tools.interference.positional_tokens_contexts_by_sent import print_positions
from tools.miscellaneous.pronouns_freq import print_pronoun_frequencies
from tools.miscellaneous.punct_analysis import display_punctuation_analysis
from tools.normalisation.repetition import print_word_occurrences_table
from tools.explicitation.sci_dm_analysis import print_dm_analysis_results
from tools.core.utils import wait_for_enter_to_analyze, wait_for_enter_to_choose_opt, display_morphological_annotation, \
    display_grammemes, display_position_explanation, get_syntactic_annotation, display_syntactic_annotation, \
    choose_universal

console = Console()
init(autoreset=True)


class SaveToDatabase:
    def __init__(self, db_name=None):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.connect_db()
        self.create_tables()

    def connect_db(self):
        """Подключение к базе данных SQLite или создание новой базы данных."""
        if self.db_name:
            self.connection = sq.connect(self.db_name)
            self.cursor = self.connection.cursor()

    def __enter__(self):
        # Открываем соединение с базой данных и возвращаем объект для использования в блоке with
        self.connect_db()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Закрываем соединение с базой данных
        if self.connection:
            self.connection.commit()
            self.connection.close()
        self.connection = None
        self.cursor = None

    def get_comparable_dbs(self, db_list):
        dbs_to_compare = []
        for db in db_list:
            self.db_name = db
            self.connect_db()
            self.cursor.execute("SELECT COUNT(*) FROM Text_Passport")
            num_texts = self.cursor.fetchone()[0]
            if num_texts > 0:
                dbs_to_compare.append(self.db_name)
        return dbs_to_compare

    def display_corpus_info(self, choice=None):
        """Отображает информацию о корпусе текстов"""
        # Извлечение количества текстов
        if choice:
            dbs_to_compare = []
            option_choice = None
            if choice == 'all':
                dbs_to_compare = self.get_comparable_dbs(
                    [NON_TRANSLATED_DB_NAME, MACHINE_TRANSLATED_DB_NAME, HUMAN_TRANSLATED_DB_NAME])
            elif choice == 'auth_mt':
                dbs_to_compare = self.get_comparable_dbs([NON_TRANSLATED_DB_NAME, MACHINE_TRANSLATED_DB_NAME])
            elif choice == 'auth_ht':
                dbs_to_compare = self.get_comparable_dbs([NON_TRANSLATED_DB_NAME, HUMAN_TRANSLATED_DB_NAME])
            elif choice == 'mt_ht':
                dbs_to_compare = self.get_comparable_dbs([MACHINE_TRANSLATED_DB_NAME, HUMAN_TRANSLATED_DB_NAME])

            if len(dbs_to_compare) < 2:
                print(f'Тексты содержатся только в базе "{dbs_to_compare}". Сравнение невозможно.')
                return

            option_choice = choose_universal()

            if option_choice == '1':
                comparison_results = {}
                for db in dbs_to_compare:
                    self.db_name = db
                    self.connect_db()
                    self.display_simplification_features_for_corpus(
                        comparison=True,
                        comparison_results=comparison_results
                    )
                self.print_simpl_comparison_table(comparison_results)

            elif option_choice == '2':
                comparison_results = {}
                print(
                    Fore.LIGHTRED_EX + Style.BRIGHT + "Пожалуйста, подождите.\n")
                for db in dbs_to_compare:
                    self.db_name = db
                    self.connect_db()
                    self.display_normalisation_features_for_corpus(
                        comparison=True,
                        comparison_results=comparison_results
                    )
                    # Затем добавляем расчет PMI
                    self.calculate_pmi_for_corpus(
                        comparison=True,
                        comparison_results=comparison_results
                    )

                self.print_normalisation_comparison_table(comparison_results)

            elif option_choice == '3':
                comparison_results = {}
                for db in dbs_to_compare:
                    self.db_name = db
                    self.connect_db()
                    self.display_explicitation_features_for_corpus(
                        comparison=True,
                        comparison_results=comparison_results
                    )
                self.print_explicitation_comparison_table(comparison_results)

            elif option_choice == '4':
                comparison_results = {}
                for db in dbs_to_compare:
                    self.db_name = db
                    self.connect_db()
                    self.display_interference_features_for_corpus(
                        comparison=True,
                        comparison_results=comparison_results
                    )
                # print(comparison_results)
                self.print_ngrams_comparison_table(comparison_results)

            elif option_choice == '5':
                comparison_results = {}
                for db in dbs_to_compare:
                    self.db_name = db
                    self.connect_db()
                    self.display_miscellaneous_features_for_corpus(
                        comparison=True,
                        comparison_results=comparison_results

                    )
                self.print_miscellaneous_comparison_table(comparison_results)
        else:
            corpus_name = ''
            if self.db_name == NON_TRANSLATED_DB_NAME:
                corpus_name = AUTH_CORPUS_NAME
            elif self.db_name == MACHINE_TRANSLATED_DB_NAME:
                corpus_name = MT_CORPUS_NAME
            elif self.db_name == HUMAN_TRANSLATED_DB_NAME:
                corpus_name = HT_CORPUS_NAME

            self.cursor.execute("SELECT COUNT(*) FROM Text_Passport")
            num_texts = self.cursor.fetchone()[0]
            if num_texts > 0:
                print("\n" + Fore.LIGHTWHITE_EX + "*" * 100)
                print(
                    Fore.GREEN + Style.BRIGHT + "                      ВЫБРАН" + Fore.LIGHTGREEN_EX
                    + Style.BRIGHT + f" {corpus_name}" + Fore.RESET)
                print(Fore.LIGHTWHITE_EX + "*" * 100)
                print(
                    Fore.GREEN + Style.BRIGHT + "\nВСЕГО ТЕКСТОВ В ВЫБРАННОМ КОРПУСЕ:"
                    + Fore.LIGHTGREEN_EX + Style.BRIGHT + f" {num_texts}" + Fore.RESET)

                option_choice = choose_universal()
                if option_choice == "1":
                    self.display_simplification_features_for_corpus()

                elif option_choice == "2":
                    self.display_normalisation_features_for_corpus()
                    self.calculate_pmi_for_corpus()

                elif option_choice == "3":
                    self.display_explicitation_features_for_corpus()

                elif option_choice == "4":
                    self.display_interference_features_for_corpus()

                elif option_choice == "5":
                    self.display_miscellaneous_features_for_corpus()

                elif option_choice == "6":
                    print(Fore.GREEN + "Выход из программы." + Fore.RESET)
                else:
                    print(
                        Fore.LIGHTRED_EX + Style.BRIGHT + "Неправильный выбор. Пожалуйста, выберите один из предложенных вариантов.\n" + Fore.RESET)

            else:

                print(
                    Fore.LIGHTGREEN_EX + Style.BRIGHT + f"\n{corpus_name}" + Fore.GREEN + Style.BRIGHT + " НЕ СОДЕРЖИТ НИ ОДНОГО ТЕКСТА" + Fore.RESET)
                wait_for_enter_to_choose_opt()

    def calculate_pmi_for_corpus(self, comparison=False, comparison_results=None):
        """Выполняет подсчет PMI для корпуса текстов"""
        if not comparison:
            print("\n" + Fore.LIGHTWHITE_EX + "*" * 100)
            print(
                Fore.GREEN + Style.BRIGHT + "               c         АНАЛИЗ " + Fore.LIGHTGREEN_EX + Style.BRIGHT + "ПОКАЗАТЕЛЯ PMI" + Fore.GREEN + Style.BRIGHT + " ДЛЯ КОРПУСА" + Fore.RESET)
            print(Fore.LIGHTWHITE_EX + "*" * 100)

            print(
                Fore.GREEN + Style.BRIGHT + "\nДалее будет проведен подсчет PMI всех рядом"
                                            "стоящих друг с другом (word1_word2) биграммов в "
                                            "тексте.")
            print(
                Fore.LIGHTGREEN_EX + Style.BRIGHT + "ВНИМАНИЕ! Точность подсчета PMI напрямую зависит от "
                                                    "размера корпуса.При небольшом размере корпуса\n"
                                                    "высока вероятность получить искусственно завышенные "
                                                    "значения PMI. Случайные редкие словосочетания\n"
                                                    "могут выявить высокие значения PMI, что будет говорить "
                                                    "не о сильной ассоциативной связи между\n"
                                                    "словами, а о недостаточно большом размере корпуса.\n"
                                                    "\nПри большом размере корпуса подсчет PMI"
                                                    " может занять некоторое время."
            )
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Пожалуйста, подождите.\n")

        # Собираем тексты для подсчета PMI
        self.cursor.execute("SELECT text FROM Text_Passport")
        texts = self.cursor.fetchall()
        corpus_set = set(text[0] for text in texts)

        pmi_values, total_above_zero, normalized_bigrams_above_zero = calculate_pmi(
            corpus_set=corpus_set)

        if comparison and comparison_results is not None:
            comparison_results[self.db_name]['normalized_bigrams_above_zero'] = normalized_bigrams_above_zero
            comparison_results[self.db_name]['total_above_zero'] = total_above_zero

        else:
            print(
                Fore.GREEN + Style.BRIGHT + f"\nPMI БИГРАММОВ КОРПУСА" + Fore.RESET)
            print(
                Fore.LIGHTGREEN_EX + Style.BRIGHT + f'Всего найдено {total_above_zero} биграммов с PMI > 0.')
            print(
                Fore.LIGHTGREEN_EX + Style.BRIGHT + f'Нормализованная частота биграммов с PMI>0: '
                                                    f'{normalized_bigrams_above_zero}.')
            while True:
                print(
                    Fore.GREEN + Style.BRIGHT + "\nОтобразить биграммы и их PMI(y/n)?")
                show_bigrams_pmi = input()
                if show_bigrams_pmi.lower() == 'y':
                    print(
                        Fore.LIGHTRED_EX + Style.BRIGHT + "\nВнимание! Вывод значений PMI для всех биграммов может занять"
                                                          " много места на экране. \nБиграммы будут представлены в лемматизированном виде.")
                    display_pmi_table(pmi_values)
                    wait_for_enter_to_choose_opt()
                    break
                elif show_bigrams_pmi.lower() == 'n':
                    break
                else:
                    print(
                        Fore.LIGHTRED_EX + Style.BRIGHT + "Неверный выбор. Пожалуйста, попробуйте снова.")
                    continue

    def display_texts(self):
        """Отображает все тексты с их порядковыми номерами и
         позволяет выбрать один для отображения подробной информации."""
        texts = self.fetch_text_passport()

        while True:
            print(Fore.GREEN + Style.BRIGHT + "\nСПИСОК ДОСТУПНЫХ ТЕКСТОВ:" + Fore.RESET)
            print(Fore.LIGHTBLACK_EX + f"0. Выйти в главное меню")
            for idx, text in enumerate(texts, 1):
                text_id, title = text[0], text[2]
                print(Fore.GREEN + Style.BRIGHT + f"{idx}." + Fore.BLACK + Style.NORMAL + f"{title.capitalize()}")
            try:
                choice = int(input(Fore.GREEN + Style.BRIGHT + "Введите номер текста для отображения "
                                                               "информации: \n" + Fore.RESET)) - 1
                if choice == -1:
                    break

                elif 0 <= choice < len(texts):
                    selected_text = texts[choice]
                    selected_text_id = selected_text[0]
                    self.display_text_info(selected_text_id)
                    break
                else:
                    print(
                        Fore.LIGHTRED_EX + Style.BRIGHT + "Ошибка: Выбран неверный номер текста. Пожалуйста, попробуйте снова." + Fore.RESET)
            except ValueError:
                print(Fore.LIGHTRED_EX + Style.BRIGHT + "Пожалуйста, введите числовое значение.\n" + Fore.RESET)

    def display_text_info(self, text_id):
        """Отображает информацию о конкретном тексте по его ID."""
        text_info = self.fetch_text_passport(text_id)

        if text_info:
            text_info = text_info[0]
            print(
                Fore.GREEN + Style.BRIGHT + f"\n                 ПАСПОРТ ТЕКСТА {text_info[0]} " + Fore.RESET)

            table = Table()

            table.add_column("Поле", no_wrap=True, style="bold", )
            table.add_column("Значение", justify="center", min_width=20)

            table.add_row("Название", text_info[2])
            table.add_row("Предметная область", text_info[3])
            table.add_row("Ключевые слова", text_info[4])
            table.add_row("Год публикации", str(text_info[5]))
            table.add_row("Место публикации (журнал)", text_info[6])
            table.add_row("Автор(ы)", text_info[7])
            table.add_row("Пол автора(ов)", text_info[8])
            table.add_row("Год рождения автора(ов)", text_info[9])
            console.print(table)
            wait_for_enter_to_analyze()

            exit_loop = False
            while True:
                print(Fore.GREEN + Style.BRIGHT + "Выберите опцию: ")
                print(Fore.BLACK + " 1. Текст статьи")
                print(Fore.BLACK + " 2. Морфологическая разметка")
                print(Fore.BLACK + " 3. Синтаксическая разметка")
                print(Fore.BLACK + " 4. Анализ индикаторов характеристики Simplification")
                print(Fore.BLACK + " 5. Анализ индикаторов характеристики Normalisation")
                print(Fore.BLACK + " 6. Анализ индикаторов характеристики Explicitation")
                print(Fore.BLACK + " 7. Анализ индикаторов характеристики Interference")
                print(Fore.BLACK + " 8. Анализ остальных индикаторов")
                print(Fore.BLACK + " 9. Удалить запись о данном тексте из БД")
                print(Fore.LIGHTBLACK_EX + " 10. Выйти в главное меню")

                choice = input(
                    Fore.GREEN + Style.BRIGHT + "Выберите, какую информацию о тексте"
                                                " хотите посмотреть.\n " + Fore.RESET)

                if choice == "1":
                    print(
                        Fore.GREEN + Style.BRIGHT + "ТЕКСТ: " + Fore.LIGHTGREEN_EX +
                        Style.BRIGHT + f"\n{text_info[1]}")
                    wait_for_enter_to_choose_opt()
                elif choice == "2":
                    self.display_morphological_annotation(text_id)
                    wait_for_enter_to_choose_opt()
                elif choice == "3":
                    synt_annot = get_syntactic_annotation(text=text_info[1])
                    display_syntactic_annotation(synt_annot)
                    wait_for_enter_to_choose_opt()
                elif choice == "4":
                    self.display_simplification_analysis(text_id)
                    wait_for_enter_to_choose_opt()
                elif choice == "5":
                    self.display_normalisation_analysis(text_id)
                    wait_for_enter_to_choose_opt()
                elif choice == "6":
                    self.display_explicitation_analysis(text_id)
                    wait_for_enter_to_choose_opt()
                elif choice == "7":
                    self.display_interference_analysis(text_id)
                    wait_for_enter_to_choose_opt()
                elif choice == "8":
                    self.display_miscellaneous_features_analysis(text_id)
                    wait_for_enter_to_choose_opt()
                elif choice == "9":
                    while True:
                        confirm = input(
                            Fore.LIGHTRED_EX + Style.BRIGHT + "Вы уверены, что хотите удалить запись об этом тексте (y/n)?\nЭто действие будет не отменить.\n" + Fore.RESET).lower()
                        if confirm == 'y':
                            self.delete_text_from_corpus(text_id)
                            exit_loop = True
                            break
                        elif confirm == 'n':
                            print(Fore.GREEN + "Удаление отменено." + Fore.RESET)
                            break
                        else:
                            print(
                                Fore.LIGHTRED_EX + Style.BRIGHT + "\nПожалуйста, введите 'y' для удаления или 'n' для отмены." + Fore.RESET)

                elif choice == "10":
                    print("Выход из программы.")
                    break

                if exit_loop:
                    break

        else:
            print("Текст с таким ID не найден.")

    def create_tables(self):
        if self.db_name:
            """Создание таблиц для хранения результатов анализа текста."""
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Text_Passport (
            text_id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            title TEXT NOT NULL,
            subject_area TEXT,
            keywords TEXT,
            publication_year INTEGER NOT NULL,
            published_in TEXT,
            authors TEXT,
            author_gender TEXT,
            author_birth_year TEXT
            )""")

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Simplification_features(
            text_id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            lexical_density REAL NOT NULL,
            
            ttr_lex_variety REAL NOT NULL,
            log_ttr_lex_variety REAL NOT NULL,
            modified_lex_variety REAL NOT NULL,
            
            mean_word_length REAL NOT NULL,
            
            syllable_ratio REAL NOT NULL,
            total_syllables_count INTEGER NOT NULL,
            
            tokens_mean_sent_length REAL NOT NULL,
            chars_mean_sent_length REAL NOT NULL,
            
            mean_word_rank_1 REAL NOT NULL,
            mean_word_rank_2 REAL NOT NULL,
            
            
            most_freq_words TEXT NOT NULL,
            types_counts TEXT NOT NULL,
            
            all_tokens_count REAL NOT NULL, 
            alpha_tokens_count REAL NOT NULL,
            all_punct_tokens_count REAL NOT NULL
            )""")

            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Normalisation_features(
            text_id INTEGER PRIMARY KEY AUTOINCREMENT,
            repetition REAL NOT NULL,
            repeated_content_words_count TEXT NOT NULL,
            repeated_content_words REAL NOT NULL,
            total_word_tokens REAL NOT NULL
            )''')

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Explicitation_features (
            text_id INTEGER PRIMARY KEY AUTOINCREMENT,
            explicit_naming_ratio REAL,
            single_naming REAL,
            
            mean_multiple_naming REAL,
            single_entities TEXT,
            single_entities_count REAL,
            multiple_entities TEXT,
            multiple_entities_count REAL,
            
            
            named_entities TEXT,
            named_entities_count REAL,
            total_tokens_with_dms REAL,
            sci_markers_total_count REAL,
            found_sci_dms TEXT,
            markers_counts TEXT,
            
            topic_intro_dm_count REAL,
            topic_intro_dm_in_ord TEXT,
            topic_intro_dm_freq  REAL,
            
            info_sequence_count REAL,
            info_sequence_in_ord TEXT,
            info_sequence_freq REAL,
            
            illustration_dm_count REAL,
            illustration_dm_in_ord TEXT,
            illustration_dm_freq REAL,
            
            material_sequence_count REAL,
            material_sequence_in_ord TEXT,
            material_sequence_freq REAL,
            
            
            conclusion_dm_count REAL,
            conclusion_dm_in_ord TEXT,
            conclusion_dm_freq REAL,
            
            
            intro_new_addit_info_count REAL,
            intro_new_addit_info_in_ord TEXT,
            intro_new_addit_info_freq REAL,
            
            
            info_explanation_or_repetition_count REAL,
            info_explanation_or_repetition_in_ord TEXT,
            info_explanation_or_repetition_freq REAL,
            
            
            contrast_dm_count REAL,
            contrast_dm_in_ord TEXT,
            contrast_dm_freq REAL,
            
            examples_introduction_dm_count REAL,
            examples_introduction_dm_in_ord TEXT,
            examples_introduction_dm_freq REAL,
            
            author_opinion_count REAL,
            author_opinion_in_ord TEXT,
            author_opinion_freq REAL,
            
            author_attitude_count REAL,
            author_attitude_in_ord TEXT,
            author_attitude_freq REAL,
            
            high_certainty_modal_words_count REAL,
            high_certainty_modal_words_in_ord TEXT,
            high_certainty_modal_words_freq REAL,
            
            moderate_certainty_modal_words_count REAL,
            moderate_certainty_modal_words_in_ord TEXT,
            moderate_certainty_modal_words_freq REAL,
            
            uncertainty_modal_words_count REAL,
            uncertainty_modal_words_in_ord TEXT,
            uncertainty_modal_words_freq REAL,
            
            call_to_action_dm_count REAL,
            call_to_action_dm_in_ord TEXT,
            call_to_action_dm_freq REAL,
            
            joint_action_count REAL,
            joint_action_in_ord TEXT,
            joint_action_freq REAL,
            
            putting_emphasis_dm_count REAL,
            putting_emphasis_dm_in_ord TEXT,
            putting_emphasis_dm_freq REAL,
            
            refer_to_background_knowledge_count REAL,
            refer_to_background_knowledge_in_ord TEXT,
            refer_to_background_knowledge_freq REAL
            ) """)

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Interference_features(
            text_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pos_unigrams_counts TEXT NOT NULL,
            pos_unigrams_freq TEXT NOT NULL,
            pos_bigrams_counts  TEXT NOT NULL,
            pos_bigrams_freq  TEXT NOT NULL,
            pos_trigrams_counts  TEXT NOT NULL,
            pos_trigrams_freq  TEXT NOT NULL,
            
            char_unigram_counts TEXT NOT NULL,
            char_unigram_freq TEXT NOT NULL,
            char_bigram_counts TEXT NOT NULL,
            char_bigram_freq TEXT NOT NULL,
            char_trigram_counts TEXT NOT NULL,
            char_trigram_freq TEXT NOT NULL,
            
            token_positions_normalized_frequencies TEXT NOT NULL,
            token_positions_counts  TEXT NOT NULL,
            token_positions_in_sent TEXT NOT NULL,
            
            func_w_trigrams_freqs TEXT NOT NULL,
            func_w_trigram_with_pos_counts TEXT NOT NULL,
            func_w_full_contexts TEXT NOT NULL
                   )""")

            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Miscellaneous_features(
            text_id INTEGER PRIMARY KEY AUTOINCREMENT,
            func_words_freq TEXT NOT NULL,
            func_words_counts TEXT NOT NULL,
            
            pers_possessive_pronouns_frequencies TEXT NOT NULL,
            pers_possessive_pronouns_counts TEXT NOT NULL,
            
            reflexive_pronoun_frequencies TEXT NOT NULL,
            reflexive_pronoun_counts TEXT NOT NULL,
    
            demonstrative_pronouns_frequencies TEXT NOT NULL,
            demonstrative_pronouns_counts TEXT NOT NULL,
            
            defining_pronouns_frequencies TEXT NOT NULL,
            defining_pronouns_counts TEXT NOT NULL,
            
            relative_pronouns_frequencies TEXT NOT NULL,
            relative_pronouns_counts TEXT NOT NULL,
    
            indefinite_pronouns_frequencies TEXT NOT NULL,
            indefinite_pronouns_counts TEXT NOT NULL,
    
            negative_pronouns_frequencies TEXT NOT NULL,
            negative_pronouns_counts TEXT NOT NULL,
            
            punct_marks_normalized_frequency TEXT NOT NULL,
            punct_marks_to_all_punct_frequency TEXT NOT NULL,
            punctuation_counts TEXT NOT NULL,
            
            passive_to_all_v_ratio REAL NOT NULL,
            passive_verbs TEXT NOT NULL,
            passive_verbs_count INTEGER NOT NULL,
            all_verbs TEXT NOT NULL,
            all_verbs_count INTEGER NOT NULL,
            
            readability_index REAL NOT NULL
            )''')

            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Morphological_annotation (
            text_id INTEGER PRIMARY KEY AUTOINCREMENT,
            morph_annotation TEXT NOT NULL
            )''')

            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Syntactic_annotation (
            text_id INTEGER PRIMARY KEY AUTOINCREMENT,
            syntactic_annotation TEXT NOT NULL
            )''')

            self.connection.commit()

    def insert_morphological_annotation(self, morph_annotation):
        """Сохраняет морфологическую разметку в базу данных."""
        self.cursor.execute("""
            INSERT INTO Morphological_annotation (morph_annotation)
            VALUES (?)
        """, (morph_annotation,))
        self.connection.commit()

    def insert_syntactic_annotation(self, syntactic_annotation):
        """Сохраняет синтаксическую разметку в базу данных."""
        self.cursor.execute("""
            INSERT INTO Syntactic_annotation (syntactic_annotation)
            VALUES (?)
        """, (syntactic_annotation,))
        self.connection.commit()

    def insert_simplification_features(self, lexical_density, ttr_lex_variety,
                                       log_ttr_lex_variety, modified_lex_variety, mean_word_length,
                                       syllable_ratio, total_syllables_count, tokens_mean_sent_length,
                                       chars_mean_sent_length, mean_word_rank_1, mean_word_rank_2, most_freq_words,
                                       types_counts, all_tokens_count, alpha_tokens_count, all_punct_tokens_count):
        """Вставка данных в таблицу Simplification_features"""
        self.cursor.execute('''
        INSERT INTO Simplification_features (lexical_density, ttr_lex_variety,
                                             log_ttr_lex_variety, modified_lex_variety, mean_word_length, 
                                             syllable_ratio, total_syllables_count, tokens_mean_sent_length, 
                                             chars_mean_sent_length,  mean_word_rank_1, mean_word_rank_2, most_freq_words,
                                             types_counts, all_tokens_count, alpha_tokens_count, all_punct_tokens_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (lexical_density, ttr_lex_variety, log_ttr_lex_variety,
              modified_lex_variety, mean_word_length, syllable_ratio, total_syllables_count,
              tokens_mean_sent_length, chars_mean_sent_length, mean_word_rank_1, mean_word_rank_2, most_freq_words,
              types_counts, all_tokens_count, alpha_tokens_count, all_punct_tokens_count))
        self.connection.commit()

    def insert_normalisation_features(self, repetition, repeated_content_words_count, repeated_content_words,
                                      total_word_tokens):
        """Вставка данных в таблицу Normalisation_features"""
        self.cursor.execute('''
        INSERT INTO Normalisation_features (repetition, repeated_content_words_count, 
        repeated_content_words, total_word_tokens)
        VALUES (?, ?, ?, ?)
        ''', (repetition, repeated_content_words_count, repeated_content_words, total_word_tokens))
        self.connection.commit()

    def insert_explicitation_features(self, explicit_naming_ratio, single_naming, mean_multiple_naming, single_entities,
                                      single_entities_count, multiple_entities, multiple_entities_count, named_entities,
                                      named_entities_count, total_tokens_with_dms,
                                      sci_markers_total_count, found_sci_dms, markers_counts,
                                      topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
                                      info_sequence_count, info_sequence_in_ord, info_sequence_freq,
                                      illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
                                      material_sequence_count, material_sequence_in_ord, material_sequence_freq,
                                      conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
                                      intro_new_addit_info_count, intro_new_addit_info_in_ord,
                                      intro_new_addit_info_freq,
                                      info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord,
                                      info_explanation_or_repetition_freq,
                                      contrast_dm_count, contrast_dm_in_ord, contrast_dm_freq,
                                      examples_introduction_dm_count, examples_introduction_dm_in_ord,
                                      examples_introduction_dm_freq,
                                      author_opinion_count, author_opinion_in_ord, author_opinion_freq,
                                      author_attitude_count, author_attitude_in_ord, author_attitude_freq,
                                      high_certainty_modal_words_count, high_certainty_modal_words_in_ord,
                                      high_certainty_modal_words_freq,
                                      moderate_certainty_modal_words_count, moderate_certainty_modal_words_in_ord,
                                      moderate_certainty_modal_words_freq,
                                      uncertainty_modal_words_count, uncertainty_modal_words_in_ord,
                                      uncertainty_modal_words_freq,
                                      call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
                                      joint_action_count, joint_action_in_ord, joint_action_freq,
                                      putting_emphasis_dm_count, putting_emphasis_dm_in_ord, putting_emphasis_dm_freq,
                                      refer_to_background_knowledge_count, refer_to_background_knowledge_in_ord,
                                      refer_to_background_knowledge_freq):
        """Вставка данных в таблицу Explicitation_features"""
        self.cursor.execute('''
        INSERT INTO Explicitation_features (explicit_naming_ratio, single_naming, mean_multiple_naming, single_entities,
                                      single_entities_count, multiple_entities, multiple_entities_count, named_entities,
                                      named_entities_count, total_tokens_with_dms,
                                      sci_markers_total_count, found_sci_dms, markers_counts,
                                      topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
                                      info_sequence_count, info_sequence_in_ord, info_sequence_freq,
                                      illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
                                      material_sequence_count, material_sequence_in_ord, material_sequence_freq,
                                      conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
                                      intro_new_addit_info_count, intro_new_addit_info_in_ord, intro_new_addit_info_freq,
                                      info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord,
                                      info_explanation_or_repetition_freq,
                                      contrast_dm_count, contrast_dm_in_ord, contrast_dm_freq,
                                      examples_introduction_dm_count, examples_introduction_dm_in_ord,
                                      examples_introduction_dm_freq,
                                      author_opinion_count, author_opinion_in_ord, author_opinion_freq,
                                      author_attitude_count,author_attitude_in_ord, author_attitude_freq,
                                      high_certainty_modal_words_count, high_certainty_modal_words_in_ord,
                                      high_certainty_modal_words_freq,
                                      moderate_certainty_modal_words_count, moderate_certainty_modal_words_in_ord,
                                      moderate_certainty_modal_words_freq,
                                      uncertainty_modal_words_count, uncertainty_modal_words_in_ord, uncertainty_modal_words_freq,
                                      call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
                                      joint_action_count, joint_action_in_ord, joint_action_freq,
                                      putting_emphasis_dm_count, putting_emphasis_dm_in_ord, putting_emphasis_dm_freq,
                                      refer_to_background_knowledge_count, refer_to_background_knowledge_in_ord, 
                                      refer_to_background_knowledge_freq
                                      
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (explicit_naming_ratio, single_naming, mean_multiple_naming, single_entities,
              single_entities_count, multiple_entities, multiple_entities_count, named_entities,
              named_entities_count, total_tokens_with_dms,
              sci_markers_total_count, found_sci_dms, markers_counts,
              topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
              info_sequence_count, info_sequence_in_ord, info_sequence_freq,
              illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
              material_sequence_count, material_sequence_in_ord, material_sequence_freq,
              conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
              intro_new_addit_info_count, intro_new_addit_info_in_ord, intro_new_addit_info_freq,
              info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord,
              info_explanation_or_repetition_freq,
              contrast_dm_count, contrast_dm_in_ord, contrast_dm_freq,
              examples_introduction_dm_count, examples_introduction_dm_in_ord,
              examples_introduction_dm_freq,
              author_opinion_count, author_opinion_in_ord, author_opinion_freq,
              author_attitude_count, author_attitude_in_ord, author_attitude_freq,
              high_certainty_modal_words_count, high_certainty_modal_words_in_ord,
              high_certainty_modal_words_freq,
              moderate_certainty_modal_words_count, moderate_certainty_modal_words_in_ord,
              moderate_certainty_modal_words_freq,
              uncertainty_modal_words_count, uncertainty_modal_words_in_ord, uncertainty_modal_words_freq,
              call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
              joint_action_count, joint_action_in_ord, joint_action_freq,
              putting_emphasis_dm_count, putting_emphasis_dm_in_ord, putting_emphasis_dm_freq,
              refer_to_background_knowledge_count, refer_to_background_knowledge_in_ord,
              refer_to_background_knowledge_freq
              ))
        self.connection.commit()

    def insert_interference_features(self, pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts,
                                     pos_bigrams_freq, pos_trigrams_counts, pos_trigrams_freq,
                                     char_unigram_counts, char_unigram_freq, char_bigram_counts,
                                     char_bigram_freq, char_trigram_counts, char_trigram_freq,
                                     token_positions_normalized_frequencies, token_positions_counts,
                                     token_positions_in_sent, func_w_trigrams_freqs, func_w_trigram_with_pos_counts,
                                     func_w_full_contexts):
        """Вставка данных в таблицу Interference_features"""
        self.cursor.execute('''
        INSERT INTO Interference_features (pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts, 
                                           pos_bigrams_freq, pos_trigrams_counts, pos_trigrams_freq, 
                                           char_unigram_counts, char_unigram_freq, char_bigram_counts, 
                                           char_bigram_freq, char_trigram_counts, char_trigram_freq, 
                                           token_positions_normalized_frequencies, 
                                           token_positions_counts, token_positions_in_sent, func_w_trigrams_freqs, 
                                           func_w_trigram_with_pos_counts, 
                                           func_w_full_contexts)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts, pos_bigrams_freq,
              pos_trigrams_counts, pos_trigrams_freq, char_unigram_counts, char_unigram_freq,
              char_bigram_counts, char_bigram_freq, char_trigram_counts, char_trigram_freq,
              token_positions_normalized_frequencies, token_positions_counts, token_positions_in_sent,
              func_w_trigrams_freqs, func_w_trigram_with_pos_counts, func_w_full_contexts))
        self.connection.commit()

    def insert_miscellaneous_features(self, func_words_freq, func_words_counts,
                                      pers_possessive_pronouns_frequencies, pers_possessive_pronouns_counts,
                                      reflexive_pronoun_frequencies, reflexive_pronoun_counts,
                                      demonstrative_pronouns_frequencies, demonstrative_pronouns_counts,
                                      defining_pronouns_frequencies, defining_pronouns_counts,
                                      relative_pronouns_frequencies, relative_pronouns_counts,
                                      indefinite_pronouns_frequencies, indefinite_pronouns_counts,
                                      negative_pronouns_frequencies, negative_pronouns_counts,
                                      punct_marks_normalized_frequency, punct_marks_to_all_punct_frequency,
                                      punctuation_counts, passive_to_all_v_ratio,
                                      passive_verbs, passive_verbs_count, all_verbs, all_verbs_count,
                                      readability_index):
        """Вставка данных в таблицу Miscellaneous_features"""
        self.cursor.execute('''
        INSERT INTO Miscellaneous_features (func_words_freq, func_words_counts,
        pers_possessive_pronouns_frequencies, pers_possessive_pronouns_counts,
        reflexive_pronoun_frequencies, reflexive_pronoun_counts,
        demonstrative_pronouns_frequencies, demonstrative_pronouns_counts,
        defining_pronouns_frequencies, defining_pronouns_counts,
        relative_pronouns_frequencies, relative_pronouns_counts,
        indefinite_pronouns_frequencies, indefinite_pronouns_counts,
        negative_pronouns_frequencies, negative_pronouns_counts,
        punct_marks_normalized_frequency, punct_marks_to_all_punct_frequency, punctuation_counts, passive_to_all_v_ratio,
        passive_verbs, passive_verbs_count, all_verbs, all_verbs_count, readability_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (func_words_freq, func_words_counts,
              pers_possessive_pronouns_frequencies, pers_possessive_pronouns_counts,
              reflexive_pronoun_frequencies, reflexive_pronoun_counts,
              demonstrative_pronouns_frequencies, demonstrative_pronouns_counts,
              defining_pronouns_frequencies, defining_pronouns_counts,
              relative_pronouns_frequencies, relative_pronouns_counts,
              indefinite_pronouns_frequencies, indefinite_pronouns_counts,
              negative_pronouns_frequencies, negative_pronouns_counts,
              punct_marks_normalized_frequency, punct_marks_to_all_punct_frequency, punctuation_counts,
              passive_to_all_v_ratio, passive_verbs, passive_verbs_count, all_verbs, all_verbs_count,
              readability_index))
        self.connection.commit()

    def insert_text_passport(self, text, title, subject_area, keywords, publication_year, published_in,
                             authors, author_gender, author_birth_year):
        """Вставка данных в таблицу Text_Passport"""
        self.cursor.execute('''
        INSERT INTO Text_Passport (text, title, subject_area, keywords, publication_year, published_in,
         authors, author_gender, author_birth_year)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (text, title, subject_area, keywords, publication_year, published_in,
              authors, author_gender, author_birth_year))
        self.connection.commit()

    def fetch_text_passport(self, text_id=None):
        """Извлечение данных паспорта текста из базы данных.

        :param text_id: (int или None) ID текста, для которого нужно извлечь данные.
                        Если None, извлекаются все данные.
        :return: Данные паспорта текста в виде списка кортежей.
        """
        self.cursor = self.connection.cursor()
        if text_id is None:
            self.cursor.execute("SELECT * FROM text_passport")
        else:
            self.cursor.execute("SELECT * FROM text_passport WHERE text_id = ?", (text_id,))
        return self.cursor.fetchall()

    def display_simplification_analysis(self, text_id):
        """Извлечение и отображение результатов анализа упрощения текста по его ID."""
        self.cursor.execute("""
            SELECT lexical_density, ttr_lex_variety, log_ttr_lex_variety, modified_lex_variety,
                   mean_word_length, syllable_ratio, total_syllables_count, tokens_mean_sent_length,
                   chars_mean_sent_length, mean_word_rank_1, mean_word_rank_2, most_freq_words
            FROM Simplification_features
            WHERE text_id = ?
        """, (text_id,))

        simplification_data = self.cursor.fetchone()

        if simplification_data:
            (lexical_density, ttr_lex_variety, log_ttr_lex_variety, modified_lex_variety,
             mean_word_length, syllable_ratio, total_syllables_count, tokens_mean_sent_length,
             chars_mean_sent_length, mean_word_rank_1, mean_word_rank_2, most_freq_words) = simplification_data

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.GREEN + Style.BRIGHT + "                 РЕЗУЛЬТАТЫ АНАЛИЗА" + Fore.LIGHTGREEN_EX +
                " SIMPLIFICATION" + Fore.GREEN + f" ДЛЯ ТЕКСТА {text_id}")
            print(Fore.LIGHTWHITE_EX + "*" * 80)
            wait_for_enter_to_analyze()

            table = Table()

            table.add_column("Показатель", no_wrap=True, style="bold")
            table.add_column("Значение", min_width=30)

            table.add_row("Лексическая плотность", f"{lexical_density:.2f}%")
            table.add_row("\nЛексическая вариативность (TTR)", f"\n{ttr_lex_variety:.2f}%")
            table.add_row("Логарифмический TTR", f"{log_ttr_lex_variety:.2f}%")
            table.add_row("TTR на основе уникальных типов", f"{modified_lex_variety:.2f}")
            table.add_row("\nСредняя длина слов в символах", f"\n{mean_word_length:.2f}")
            table.add_row("Средняя длина слов в слогах", f"{syllable_ratio:.2f}")
            table.add_row("Общее количество слогов", f"{total_syllables_count}")
            table.add_row("\nСредняя длина предложений в токенах", f"\n{tokens_mean_sent_length:.2f}")
            table.add_row("Средняя длина предложений в символах", f"{chars_mean_sent_length:.2f}")
            table.add_row("\nСредний ранг слов (1)", f"\n{mean_word_rank_1:.2f}")
            table.add_row("\nСредний ранг слов (2)", f"\n{mean_word_rank_1:.2f}")

            # Заменяем одинарные кавычки на двойные и удаляем возможные невалидные символы
            json_str = most_freq_words.replace("'", '"').strip()

            # Преобразуем ключи в строки
            json_str = re.sub(r'(\d+):', r'"\1":', json_str)
            # Преобразуем строку most_freq_words в словарь
            try:
                most_freq_words_dict = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(Fore.LIGHTRED_EX + Style.BRIGHT + f"Ошибка парсинга JSON: {e}" + Fore.RESET)
                return

            if "50" in most_freq_words_dict:
                top_50_words = list(most_freq_words_dict["50"].items())
                top_50_words_str = ', '.join([f"{word} ({freq:.3f})" for word, freq in top_50_words])
                table.add_row("\nНаиболее частотные 50 слов \n(и их нормализованные частоты)", '\n' + top_50_words_str)
            else:
                table.add_row("\nНаиболее частотные 50 слов \n(и их нормализованные частоты)", "\nНет данных")

            console.print(table)
        else:
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Результаты анализа SIMPLIFICATION для этого текста не найдены." +
                Fore.RESET)

    def display_normalisation_analysis(self, text_id):
        """Извлечение и отображение результатов анализа индикаторов универсалии Normalisation по его ID."""
        self.cursor.execute("""
            SELECT repetition, repeated_content_words_count, repeated_content_words, total_word_tokens
            FROM Normalisation_features
            WHERE text_id = ?
        """, (text_id,))

        normalisation_data = self.cursor.fetchone()

        if normalisation_data:
            (repetition, repeated_content_words_count, repeated_content_words, total_word_tokens) = normalisation_data

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.GREEN + Style.BRIGHT + "                 РЕЗУЛЬТАТЫ АНАЛИЗА" + Fore.LIGHTGREEN_EX +
                " NORMALISATION" + Fore.GREEN + f" ДЛЯ ТЕКСТА {text_id}")
            print(Fore.LIGHTWHITE_EX + "*" * 80)

            table = Table()

            table.add_column("Показатель", no_wrap=True, style="bold")
            table.add_column("Значение", justify="center", min_width=20)

            table.add_row("Повторяемость", f"{repetition:.2f}%")
            table.add_row("Число повторяющихся знаменательных слов", f"{repeated_content_words}")
            table.add_row("Всего токенов", f"{total_word_tokens}")
            console.print(table)
            wait_for_enter_to_analyze()

            print_word_occurrences_table(repeated_content_words_count)
        else:
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Результаты анализа нормализации для этого текста не найдены." +
                Fore.RESET)

    def display_explicitation_analysis(self, text_id):
        """Извлечение и отображение результатов анализа индикаторов универсалии Explicitation по его ID."""
        self.cursor.execute("""
            SELECT explicit_naming_ratio, single_naming, mean_multiple_naming, single_entities,
                   single_entities_count, multiple_entities, multiple_entities_count, named_entities,
                   named_entities_count,
                   sci_markers_total_count, markers_counts,
                   topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
                   info_sequence_count, info_sequence_in_ord, info_sequence_freq,
                   illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
                   material_sequence_count, material_sequence_in_ord, material_sequence_freq,
                   conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
                   intro_new_addit_info_count, intro_new_addit_info_in_ord, intro_new_addit_info_freq,
                   info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord, info_explanation_or_repetition_freq,
                   contrast_dm_count, contrast_dm_in_ord, contrast_dm_freq,
                   examples_introduction_dm_count, examples_introduction_dm_in_ord, examples_introduction_dm_freq,
                   author_opinion_count, author_opinion_in_ord, author_opinion_freq,
                   author_attitude_count, author_attitude_in_ord, author_attitude_freq,
                   high_certainty_modal_words_count, high_certainty_modal_words_in_ord, high_certainty_modal_words_freq,
                   moderate_certainty_modal_words_count, moderate_certainty_modal_words_in_ord, moderate_certainty_modal_words_freq,
                   uncertainty_modal_words_count, uncertainty_modal_words_in_ord, uncertainty_modal_words_freq,
                   call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
                   joint_action_count, joint_action_in_ord, joint_action_freq,
                   putting_emphasis_dm_count, putting_emphasis_dm_in_ord, putting_emphasis_dm_freq,
                   refer_to_background_knowledge_count, refer_to_background_knowledge_in_ord, refer_to_background_knowledge_freq
            FROM Explicitation_features
            WHERE text_id = ?
        """, (text_id,))

        explicitation_data = self.cursor.fetchone()

        if explicitation_data:
            (explicit_naming_ratio, single_naming, mean_multiple_naming, single_entities,
             single_entities_count, multiple_entities, multiple_entities_count, named_entities,
             named_entities_count,
             sci_markers_total_count, markers_counts,
             topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
             info_sequence_count, info_sequence_in_ord, info_sequence_freq,
             illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
             material_sequence_count, material_sequence_in_ord, material_sequence_freq,
             conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
             intro_new_addit_info_count, intro_new_addit_info_in_ord, intro_new_addit_info_freq,
             info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord,
             info_explanation_or_repetition_freq,
             contrast_dm_count, contrast_dm_in_ord, contrast_dm_freq,
             examples_introduction_dm_count, examples_introduction_dm_in_ord, examples_introduction_dm_freq,
             author_opinion_count, author_opinion_in_ord, author_opinion_freq,
             author_attitude_count, author_attitude_in_ord, author_attitude_freq,
             high_certainty_modal_words_count, high_certainty_modal_words_in_ord, high_certainty_modal_words_freq,
             moderate_certainty_modal_words_count, moderate_certainty_modal_words_in_ord,
             moderate_certainty_modal_words_freq,
             uncertainty_modal_words_count, uncertainty_modal_words_in_ord, uncertainty_modal_words_freq,
             call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
             joint_action_count, joint_action_in_ord, joint_action_freq,
             putting_emphasis_dm_count, putting_emphasis_dm_in_ord, putting_emphasis_dm_freq,
             refer_to_background_knowledge_count, refer_to_background_knowledge_in_ord,
             refer_to_background_knowledge_freq) = explicitation_data

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.GREEN + Style.BRIGHT + "                 РЕЗУЛЬТАТЫ АНАЛИЗА" + Fore.LIGHTGREEN_EX +
                " EXPLICITATION" + Fore.GREEN + f" ДЛЯ ТЕКСТА {text_id}")
            print(Fore.LIGHTWHITE_EX + "*" * 80)

            table = Table()

            table.add_column("Показатель", style="bold")
            table.add_column("Значение", justify="center", min_width=30)

            table.add_row("Explicit naming", f"{explicit_naming_ratio:.2f}%")
            table.add_row("Single naming", f"{single_naming:.2f}%")
            table.add_row("Средняя длина именованных сущностей \n(в токенах)", f"{mean_multiple_naming:.2f}")

            # Выводим таблицу
            console.print(table)
            wait_for_enter_to_analyze()
            display_entities(named_entities, named_entities_count)
            wait_for_enter_to_analyze()
            print_dm_analysis_results(sci_markers_total_count, markers_counts,
                                      topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
                                      info_sequence_count, info_sequence_in_ord, info_sequence_freq,
                                      illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
                                      material_sequence_count, material_sequence_in_ord, material_sequence_freq,
                                      conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
                                      intro_new_addit_info_count, intro_new_addit_info_in_ord,
                                      intro_new_addit_info_freq,
                                      info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord,
                                      info_explanation_or_repetition_freq,
                                      contrast_dm_count, contrast_dm_in_ord, contrast_dm_freq,
                                      examples_introduction_dm_count, examples_introduction_dm_in_ord,
                                      examples_introduction_dm_freq,
                                      author_opinion_count, author_opinion_in_ord, author_opinion_freq,
                                      author_attitude_count, author_attitude_in_ord, author_attitude_freq,
                                      high_certainty_modal_words_count, high_certainty_modal_words_in_ord,
                                      high_certainty_modal_words_freq,
                                      moderate_certainty_modal_words_count, moderate_certainty_modal_words_in_ord,
                                      moderate_certainty_modal_words_freq,
                                      uncertainty_modal_words_count, uncertainty_modal_words_in_ord,
                                      uncertainty_modal_words_freq,
                                      call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
                                      joint_action_count, joint_action_in_ord, joint_action_freq,
                                      putting_emphasis_dm_count, putting_emphasis_dm_in_ord, putting_emphasis_dm_freq,
                                      refer_to_background_knowledge_count, refer_to_background_knowledge_in_ord,
                                      refer_to_background_knowledge_freq)
        else:
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Результаты анализа экспликации для этого текста не найдены." +
                Fore.RESET)

    def display_interference_analysis(self, text_id):
        """Извлечение и отображение результатов анализа индикаторов универсалии Interference по его ID."""
        self.cursor.execute("""
            SELECT pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts, pos_bigrams_freq, 
                   pos_trigrams_counts, pos_trigrams_freq, char_unigram_counts, char_unigram_freq,
                   char_bigram_counts, char_bigram_freq, char_trigram_counts, char_trigram_freq, 
                   token_positions_counts, token_positions_normalized_frequencies, token_positions_in_sent, 
                   func_w_trigrams_freqs, func_w_trigram_with_pos_counts, func_w_full_contexts
            FROM Interference_features
            WHERE text_id = ?
        """, (text_id,))

        interference_data = self.cursor.fetchone()

        if interference_data:
            (pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts, pos_bigrams_freq,
             pos_trigrams_counts, pos_trigrams_freq, char_unigram_counts, char_unigram_freq,
             char_bigram_counts, char_bigram_freq, char_trigram_counts, char_trigram_freq,
             token_positions_counts, token_positions_normalized_frequencies, token_positions_in_sent,
             func_w_trigrams_freqs, func_w_trigram_with_pos_counts, func_w_full_contexts) = interference_data

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.GREEN + Style.BRIGHT + "                 РЕЗУЛЬТАТЫ АНАЛИЗА" + Fore.LIGHTGREEN_EX +
                " INTERFERENCE" + Fore.GREEN + f" ДЛЯ ТЕКСТА {text_id}")
            print(Fore.LIGHTWHITE_EX + "*" * 80)

            print(Fore.GREEN + Style.BRIGHT + "\n                      ЧАСТОТЫ ЧАСТЕРЕЧНЫХ N-ГРАММОВ")
            display_grammemes()
            display_ngrams_summary(pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts, pos_bigrams_freq,
                                   pos_trigrams_counts, pos_trigrams_freq)

            print(Fore.GREEN + Style.BRIGHT + "\n                      ЧАСТОТЫ БУКВЕННЫХ N-ГРАММОВ")
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Внимание! N-граммы '<' и '>' используются для обозначания начала и конца \nслов соответственно.\n" + Fore.RESET)
            display_ngrams_summary(char_unigram_counts, char_unigram_freq, char_bigram_counts, char_bigram_freq,
                                   char_trigram_counts, char_trigram_freq)

            print(Fore.GREEN + Style.BRIGHT + "\n                      ПОЗИЦИОННАЯ ЧАСТОТА ТОКЕНОВ")
            print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "Учитываются предложения, длина которых больше 5 токенов.")

            print_frequencies(token_positions_normalized_frequencies, token_positions_counts)
            print(
                Fore.GREEN + Style.BRIGHT + "\n             ТОКЕНЫ И ИХ ЧАСТИ РЕЧИ НА РАЗНЫХ ПОЗИЦИЯХ В ПРЕДЛОЖЕНИИ"
                + Fore.RESET)
            print(
                Fore.LIGHTGREEN_EX + Style.BRIGHT + "* Выводятся контексты предложений, длиннее 5 токенов."
                + Fore.RESET)
            wait_for_enter_to_analyze()
            print_positions(token_positions_in_sent)
            print_trigram_tables_with_func_w(func_w_trigrams_freqs, func_w_trigram_with_pos_counts,
                                             func_w_full_contexts, True)
        else:
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Результаты анализа интерференции для этого текста не найдены."
                + Fore.RESET)

    def display_miscellaneous_features_analysis(self, text_id):

        self.cursor.execute("""
            SELECT func_words_freq, func_words_counts, 
            pers_possessive_pronouns_frequencies, pers_possessive_pronouns_counts,
            reflexive_pronoun_frequencies, reflexive_pronoun_counts,
            demonstrative_pronouns_frequencies, demonstrative_pronouns_counts,
            defining_pronouns_frequencies, defining_pronouns_counts,
            relative_pronouns_frequencies, relative_pronouns_counts,
            indefinite_pronouns_frequencies, indefinite_pronouns_counts,
            negative_pronouns_frequencies, negative_pronouns_counts,
            punct_marks_normalized_frequency, punct_marks_to_all_punct_frequency,punctuation_counts, 
            passive_to_all_v_ratio, passive_verbs, passive_verbs_count, all_verbs, all_verbs_count, readability_index
            FROM Miscellaneous_features
            WHERE text_id = ?
        """, (text_id,))

        miscellaneous_features_data = self.cursor.fetchone()

        if miscellaneous_features_data:
            (func_words_freq, func_words_counts,
             pers_possessive_pronouns_frequencies, pers_possessive_pronouns_counts,
             reflexive_pronoun_frequencies, reflexive_pronoun_counts,
             demonstrative_pronouns_frequencies, demonstrative_pronouns_counts,
             defining_pronouns_frequencies, defining_pronouns_counts,
             relative_pronouns_frequencies, relative_pronouns_counts,
             indefinite_pronouns_frequencies, indefinite_pronouns_counts,
             negative_pronouns_frequencies, negative_pronouns_counts,
             punct_marks_normalized_frequency,
             punct_marks_to_all_punct_frequency, punctuation_counts, passive_to_all_v_ratio,
             passive_verbs, passive_verbs_count, all_verbs, all_verbs_count,
             readability_index) = miscellaneous_features_data

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.GREEN + Style.BRIGHT + "              РЕЗУЛЬТАТЫ АНАЛИЗА" + Fore.LIGHTGREEN_EX +
                " ОСТАЛЬНЫХ ИНДИКАТОРОВ" + Fore.GREEN + f" ДЛЯ ТЕКСТА {text_id}")
            print(Fore.LIGHTWHITE_EX + "*" * 80)
            wait_for_enter_to_analyze()

            print_func_w__frequencies(func_words_freq, func_words_counts)
            wait_for_enter_to_analyze()

            print_pronoun_frequencies('pers_possessive', pers_possessive_pronouns_frequencies,
                                      pers_possessive_pronouns_counts)
            print_pronoun_frequencies('reflexive_pronoun', reflexive_pronoun_frequencies, reflexive_pronoun_counts)
            print_pronoun_frequencies('demonstrative_pronouns', demonstrative_pronouns_frequencies,
                                      demonstrative_pronouns_counts)
            print_pronoun_frequencies('defining_pronouns', defining_pronouns_frequencies, defining_pronouns_counts)

            print_pronoun_frequencies('relative_pronouns', relative_pronouns_frequencies, relative_pronouns_counts)
            print_pronoun_frequencies('indefinite_pronouns', indefinite_pronouns_frequencies,
                                      indefinite_pronouns_counts)
            print_pronoun_frequencies('negative_pronouns', negative_pronouns_frequencies, negative_pronouns_counts)

            wait_for_enter_to_analyze()
            display_punctuation_analysis(punct_marks_normalized_frequency, punct_marks_to_all_punct_frequency,
                                         punctuation_counts)
            wait_for_enter_to_analyze()
            print_passive_verbs_ratio(passive_to_all_v_ratio,
                                      passive_verbs, passive_verbs_count, all_verbs, all_verbs_count)
            wait_for_enter_to_analyze()
            display_readability_index(readability_index)

        else:
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Результаты анализа остальных индикаторов для этого текста не "
                                                  "найдены." + Fore.RESET)

    def display_morphological_annotation(self, text_id):
        """Отображает морфологическую разметку текста по его ID."""
        self.cursor.execute("""
            SELECT morph_annotation FROM Morphological_annotation WHERE text_id = ?
        """, (text_id,))
        result = self.cursor.fetchone()
        if result:
            # Преобразуем строку JSON в объект Python
            sentences_info = json.loads(result[0])
            display_morphological_annotation(sentences_info)

    def display_simplification_features_for_corpus(self, comparison=False, comparison_results=None):
        """Отображает средние показатели индикаторов универсалии Simplification."""
        # Выполняем запрос на извлечение взвешенных значений индикаторов
        self.cursor.execute('''
            SELECT 
                SUM(alpha_tokens_count * lexical_density) / SUM(alpha_tokens_count),
                SUM(alpha_tokens_count * ttr_lex_variety) / SUM(alpha_tokens_count),
                SUM(alpha_tokens_count * log_ttr_lex_variety) / SUM(alpha_tokens_count),
                SUM(alpha_tokens_count * modified_lex_variety) / SUM(alpha_tokens_count),
                SUM(alpha_tokens_count * mean_word_length) / SUM(alpha_tokens_count),
                SUM(alpha_tokens_count * syllable_ratio) / SUM(alpha_tokens_count),
                SUM(alpha_tokens_count * total_syllables_count) / SUM(alpha_tokens_count),
                SUM(alpha_tokens_count * tokens_mean_sent_length) / SUM(alpha_tokens_count),
                SUM(all_tokens_count * chars_mean_sent_length) / SUM(all_tokens_count),
                SUM(alpha_tokens_count * mean_word_rank_1) / SUM(alpha_tokens_count),
                SUM(alpha_tokens_count * mean_word_rank_2) / SUM(alpha_tokens_count)
            FROM Simplification_features
        ''')

        result = self.cursor.fetchone()

        if result:
            (avg_lexical_density, avg_ttr_lex_variety, avg_log_ttr_lex_variety, avg_modified_lex_variety,
             avg_mean_word_length, avg_syllable_ratio, avg_total_syllables_count, avg_tokens_mean_sent_length,
             avg_chars_mean_sent_length, avg_mean_word_rank_1, avg_mean_word_rank_2) = result

            if comparison:
                comparison_results[self.db_name] = {
                    "lexical_density": avg_lexical_density,
                    "ttr_lex_variety": avg_ttr_lex_variety,
                    "log_ttr_lex_variety": avg_log_ttr_lex_variety,
                    "modified_lex_variety": avg_modified_lex_variety,
                    "mean_word_length": avg_mean_word_length,
                    "syllable_ratio": avg_syllable_ratio,
                    "total_syllables_count": avg_total_syllables_count,
                    "tokens_mean_sent_length": avg_tokens_mean_sent_length,
                    "chars_mean_sent_length": avg_chars_mean_sent_length,
                    "mean_word_rank_1": avg_mean_word_rank_1,
                    "mean_word_rank_2": avg_mean_word_rank_2
                }
            else:
                print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
                print(
                    Fore.GREEN + Style.BRIGHT + '             СРЕДНИЕ ПОКАЗАТЕЛИ ХАРАКТЕРИСТИКИ' +
                    Fore.LIGHTGREEN_EX + Style.BRIGHT + ' SIMPLIFICATION')
                print(Fore.LIGHTWHITE_EX + "*" * 80)
                table = Table()

                table.add_column("Индикатор", justify="left", no_wrap=True, style="bold")
                table.add_column("Значение", justify="center", min_width=15)

                table.add_row("Лексическая плотность", f"{avg_lexical_density:.2f}%")
                table.add_row("\nЛексическая вариативность (TTR)", f"\n{avg_ttr_lex_variety:.2f}%")
                table.add_row("Логарифмический TTR", f"{avg_log_ttr_lex_variety:.2f}%")
                table.add_row("TTR на основе уникальных типов", f"{avg_modified_lex_variety:.2f}")
                table.add_row("\nСредняя длина слова (в символах)", f"\n{avg_mean_word_length:.2f}")
                table.add_row("Средняя длина слов (в слогах)", f"{avg_syllable_ratio:.2f}")
                table.add_row("Среднее количество слогов", f"{avg_total_syllables_count:.0f}")
                table.add_row("\nСредняя длина предложений (в токенах)", f"\n{avg_tokens_mean_sent_length:.2f}")
                table.add_row("Средняя длина предложений (в символах)", f"{avg_chars_mean_sent_length:.2f}")
                table.add_row("\nСредний ранг слов (1)", f"\n{avg_mean_word_rank_1:.2f}")
                table.add_row("Средний ранг слов (2)", f"{avg_mean_word_rank_2:.2f}")

                console.print(table)
                print(Fore.LIGHTWHITE_EX + "*" * 80)
                wait_for_enter_to_analyze()

            # Извлекаем types_counts и alpha_tokens_count из базы данных
            self.cursor.execute('SELECT types_counts, alpha_tokens_count FROM Simplification_features')
            types_counts_results = self.cursor.fetchall()

            # Считаем общую сумму токенов по всему корпусу
            total_tokens = 0
            combined_counts = defaultdict(int)

            # Считаем частоты слов по всему корпусу
            for row in types_counts_results:
                types_counts = json.loads(row[0])  # Преобразуем JSON обратно в словарь
                alpha_tokens_count = row[1]  # Получаем количество токенов для текущего текста
                total_tokens += alpha_tokens_count  # Суммируем общее количество токенов

                # Объединяем частоты слов
                for word, count in types_counts.items():
                    combined_counts[word] += count

            # Сортируем по частоте и берем 50 самых частотных слов
            sorted_combined_counts = sorted(combined_counts.items(), key=lambda item: item[1], reverse=True)[:50]

            if not comparison:
                print(Fore.LIGHTWHITE_EX + "*" * 80)
                print(
                    Fore.GREEN + Style.BRIGHT + '             50 НАИБОЛЕЕ ЧАСТОТНЫХ СЛОВ В КОРПУСЕ')
                print(Fore.LIGHTWHITE_EX + "*" * 80)
                table = Table()

                table.add_column("Слово", justify="left", style="bold")
                table.add_column("Частота", justify="center", min_width=15)
                print(total_tokens)

                for word, count in sorted_combined_counts:
                    normalized_freq = (count / total_tokens) * 100  # Рассчитываем нормализованную частоту
                    table.add_row(word, str(count), f"{normalized_freq:.2f}%")

                console.print(table)
                print(Fore.LIGHTWHITE_EX + "*" * 80)

                wait_for_enter_to_choose_opt()
        else:
            print(Fore.LIGHTRED_EX + "Данные о показателях Simplification отсутствуют." + Fore.RESET)

    def display_normalisation_features_for_corpus(self, comparison=False, comparison_results=None):
        """Отображение средних значений индикаторов универсалии Normalisation"""

        self.cursor.execute('''
            SELECT 
                SUM(Simplification_features.alpha_tokens_count * Normalisation_features.repetition) / SUM(Simplification_features.alpha_tokens_count),
                SUM(Simplification_features.alpha_tokens_count * Normalisation_features.repeated_content_words) / SUM(Simplification_features.alpha_tokens_count),
                SUM(Simplification_features.alpha_tokens_count * Normalisation_features.total_word_tokens) / SUM(Simplification_features.alpha_tokens_count)
            FROM Normalisation_features
            JOIN Simplification_features ON Normalisation_features.text_id = Simplification_features.text_id
        ''')

        result = self.cursor.fetchone()

        if result:
            avg_repetition, avg_repeated_content_words, avg_total_word_tokens = result
            if comparison and comparison_results is not None:
                comparison_results[self.db_name] = {
                    'avg_repetition': avg_repetition,
                    'avg_repeated_content_words': avg_repeated_content_words,
                    'avg_total_word_tokens': avg_total_word_tokens
                }
            else:
                print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
                print(
                    Fore.GREEN + Style.BRIGHT + '                СРЕДНИЕ ПОКАЗАТЕЛИ ХАРАКТЕРИСТИКИ' +
                    Fore.LIGHTGREEN_EX + Style.BRIGHT + ' NORMALISATION')
                print(Fore.LIGHTWHITE_EX + "*" * 80)
                table = Table()

                table.add_column("Показатель", justify="left", no_wrap=True, style="bold")
                table.add_column("Значение", justify="center")

                table.add_row("Повторяемость", f"{avg_repetition:.2f}%")
                table.add_row("Количество повторяющихся знаменательных слов", f"{avg_repeated_content_words:.2f}")
                table.add_row("Количество словарных токенов", f"{avg_total_word_tokens:.2f}")

                console.print(table)
                wait_for_enter_to_analyze()

    def display_explicitation_features_for_corpus(self, comparison=False, comparison_results=None):
        """Отображает средние показатели индикаторов универсалии Explicitation"""
        self.cursor.execute('''
            SELECT 
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.explicit_naming_ratio) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.single_naming) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.mean_multiple_naming) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.single_entities_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.multiple_entities_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.named_entities_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.sci_markers_total_count) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.topic_intro_dm_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.topic_intro_dm_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.info_sequence_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.info_sequence_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.illustration_dm_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.illustration_dm_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.material_sequence_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.material_sequence_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.conclusion_dm_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.conclusion_dm_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.intro_new_addit_info_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.intro_new_addit_info_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.info_explanation_or_repetition_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.info_explanation_or_repetition_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.contrast_dm_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.contrast_dm_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.examples_introduction_dm_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.examples_introduction_dm_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.author_opinion_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.author_opinion_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.author_attitude_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.author_attitude_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.high_certainty_modal_words_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.high_certainty_modal_words_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.moderate_certainty_modal_words_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.moderate_certainty_modal_words_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.uncertainty_modal_words_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.uncertainty_modal_words_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.call_to_action_dm_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.call_to_action_dm_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.joint_action_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.joint_action_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.putting_emphasis_dm_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.putting_emphasis_dm_freq) / SUM(Explicitation_features.total_tokens_with_dms),

                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.refer_to_background_knowledge_count) / SUM(Explicitation_features.total_tokens_with_dms),
                SUM(Explicitation_features.total_tokens_with_dms * Explicitation_features.refer_to_background_knowledge_freq) / SUM(Explicitation_features.total_tokens_with_dms)
            FROM Explicitation_features
        ''')

        result = self.cursor.fetchone()

        if result:
            (
                avg_explicit_naming_ratio, avg_single_naming, avg_mean_multiple_naming, avg_single_entities_count,
                avg_multiple_entities_count, avg_named_entities_count, avg_sci_markers_total_count,
                avg_topic_intro_dm_count, avg_topic_intro_dm_freq, avg_info_sequence_count, avg_info_sequence_freq,
                avg_illustration_dm_count, avg_illustration_dm_freq, avg_material_sequence_count,
                avg_material_sequence_freq, avg_conclusion_dm_count, avg_conclusion_dm_freq,
                avg_intro_new_addit_info_count, avg_intro_new_addit_info_freq, avg_info_explanation_or_repetition_count,
                avg_info_explanation_or_repetition_freq, avg_contrast_dm_count, avg_contrast_dm_freq,
                avg_examples_introduction_dm_count, avg_examples_introduction_dm_freq,
                avg_author_opinion_count, avg_author_opinion_freq,
                avg_author_attitude_count, avg_author_attitude_freq,
                avg_high_certainty_modal_words_count, avg_high_certainty_modal_words_freq,
                avg_moderate_certainty_modal_words_count, avg_moderate_certainty_modal_words_freq,
                avg_uncertainty_modal_words_count, avg_uncertainty_modal_words_freq,
                avg_call_to_action_dm_count,
                avg_call_to_action_dm_freq, avg_joint_action_count, avg_joint_action_freq,
                avg_putting_emphasis_dm_count,
                avg_putting_emphasis_dm_freq, avg_refer_to_background_knowledge_count,
                avg_refer_to_background_knowledge_freq
            ) = result

            if comparison and comparison_results is not None:
                comparison_results[self.db_name] = {
                    'explicit_naming_ratio': avg_explicit_naming_ratio,
                    'single_naming': avg_single_naming,
                    'mean_multiple_naming': avg_mean_multiple_naming,
                    'named_entities_count': avg_named_entities_count,
                    'sci_markers_total_count': avg_sci_markers_total_count,
                    'topic_intro_dm_freq': avg_topic_intro_dm_freq,
                    'info_sequence_freq': avg_info_sequence_freq,
                    'illustration_dm_freq': avg_illustration_dm_freq,
                    'material_sequence_freq': avg_material_sequence_freq,
                    'conclusion_dm_freq': avg_conclusion_dm_freq,
                    'intro_new_addit_info_freq': avg_intro_new_addit_info_freq,
                    'info_explanation_or_repetition_freq': avg_info_explanation_or_repetition_freq,
                    'contrast_dm_freq': avg_contrast_dm_freq,
                    'examples_introduction_dm_freq': avg_examples_introduction_dm_freq,
                    'author_opinion_freq': avg_author_opinion_freq,
                    'author_attitude_freq': avg_author_attitude_freq,
                    'high_certainty_modal_words_freq': avg_high_certainty_modal_words_freq,
                    'moderate_certainty_modal_words_freq': avg_moderate_certainty_modal_words_freq,
                    'uncertainty_modal_words_freq': avg_uncertainty_modal_words_freq,
                    'call_to_action_dm_freq': avg_call_to_action_dm_freq,
                    'joint_action_freq': avg_joint_action_freq,
                    'putting_emphasis_dm_freq': avg_putting_emphasis_dm_freq,
                    'refer_to_background_knowledge_freq': avg_refer_to_background_knowledge_freq
                }
            else:
                print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
                print(
                    Fore.GREEN + Style.BRIGHT + '                СРЕДНИЕ ПОКАЗАТЕЛИ ХАРАКТЕРИСТИКИ'
                    + Fore.LIGHTGREEN_EX + Style.BRIGHT + ' EXPLICITATION')
                print(Fore.LIGHTWHITE_EX + "*" * 80)

                table = Table()

                # Добавляем колонки
                table.add_column("Индикатор", justify="left", no_wrap=True, style="bold")
                table.add_column("Значение", justify="center")

                # Заполняем таблицу данными
                table.add_row("Explicit naming", f"{avg_explicit_naming_ratio:.2f}%")
                table.add_row("Single naming", f"{avg_single_naming:.2f}%")
                table.add_row("Средняя длина именованных сущностей (в токенах)", f"{avg_mean_multiple_naming:.2f}")
                table.add_row("Количество именованных сущностей", f"{avg_named_entities_count:.2f}")
                console.print(table)
                wait_for_enter_to_analyze()

                print(
                    Fore.GREEN + Style.BRIGHT + "\n           СРЕДНИЕ ПОКАЗАТЕЛИ ЧАСТОТ ДИСКУРСИВНЫХ МАРКЕРОВ "
                                                "ПО КАТЕГОРИЯМ" + Fore.RESET)
                print(
                    Fore.BLUE + Style.DIM + f"                        В среднем тексты содержат "
                                            f"{avg_sci_markers_total_count:.0F} ДМ" + Fore.RESET)

                freq_table = Table()
                freq_table.add_column("Категория ДМ\n", justify="left", no_wrap=True)
                freq_table.add_column("Абсолютная частота\n", justify="center")
                freq_table.add_column("Нормализованная частота (%)", justify="center")

                frequency_data = [
                    ("Введение в тему", avg_topic_intro_dm_count, avg_topic_intro_dm_freq),
                    ("Порядок следования информации", avg_info_sequence_count, avg_info_sequence_freq),
                    ("Иллюстративный материал", avg_illustration_dm_count, avg_illustration_dm_freq),
                    ("Порядок расположения материала", avg_material_sequence_count, avg_material_sequence_freq),
                    ("Вывод/заключение", avg_conclusion_dm_count, avg_conclusion_dm_freq),
                    ("Введение новой/доп. информации", avg_intro_new_addit_info_count, avg_intro_new_addit_info_freq),
                    ("Повтор/конкретизация информации", avg_info_explanation_or_repetition_count,
                     avg_info_explanation_or_repetition_freq),
                    ("Противопоставление", avg_contrast_dm_count, avg_contrast_dm_freq),
                    ("Введение примеров", avg_examples_introduction_dm_count, avg_examples_introduction_dm_freq),
                    ("Мнение автора", avg_author_opinion_count, avg_author_opinion_freq),
                    ("Отношение автора", avg_author_attitude_count, avg_author_attitude_freq),
                    ("Высокая степень уверенности", avg_high_certainty_modal_words_count,
                     avg_high_certainty_modal_words_freq),
                    ("Средняя степень уверенности", avg_moderate_certainty_modal_words_count,
                     avg_moderate_certainty_modal_words_freq),
                    ("Низкая степень уверенности", avg_uncertainty_modal_words_count,
                     avg_uncertainty_modal_words_freq),
                    ("Призыв к действию", avg_call_to_action_dm_count, avg_call_to_action_dm_freq),
                    ("Совместное действие", avg_joint_action_count, avg_joint_action_freq),
                    ("Акцентирование внимания", avg_putting_emphasis_dm_count, avg_putting_emphasis_dm_freq),
                    ("Отсылка к фоновым знаниям", avg_refer_to_background_knowledge_count,
                     avg_refer_to_background_knowledge_freq),
                ]

                # Фильтрация по частоте > 0
                frequency_data_filtered = [(cat, count, freq) for cat, count, freq in frequency_data if count > 0]

                # Сортировка по абсолютной частоте в порядке убывания
                frequency_data_sorted = sorted(frequency_data_filtered, key=lambda x: x[1], reverse=True)

                # Добавление строк в таблицу после сортировки
                for category_name, count, freq in frequency_data_sorted:
                    freq_table.add_row(category_name, f"{count:.3f}", f"{freq:.3f}%")

                console.print(freq_table)
                wait_for_enter_to_choose_opt()

    def display_miscellaneous_features_for_corpus(self, comparison=False, comparison_results=None):
        """Отображение взвешенных средних показателей индикаторов Miscellaneous_features."""

        # Извлечение агрегированных данных для количественных показателей
        self.cursor.execute('''
            SELECT SUM(alpha_tokens_count * passive_to_all_v_ratio) / SUM(alpha_tokens_count),
                   SUM(alpha_tokens_count * passive_verbs_count) / SUM(alpha_tokens_count),
                   SUM(alpha_tokens_count * all_verbs_count) / SUM(alpha_tokens_count),
                   SUM(alpha_tokens_count * readability_index) / SUM(alpha_tokens_count)
            FROM Miscellaneous_features
            JOIN Simplification_features ON Miscellaneous_features.text_id = Simplification_features.text_id
        ''')
        result_aggregated = self.cursor.fetchone()

        if result_aggregated:
            avg_passive_to_all_v_ratio, avg_passive_verbs_count, avg_all_verbs_count, avg_readability_index = result_aggregated

            if comparison:
                comparison_results[self.db_name] = {
                    'avg_passive_to_all_v_ratio': avg_passive_to_all_v_ratio,
                    'avg_passive_verbs_count': avg_passive_verbs_count,
                    'avg_all_verbs_count': avg_all_verbs_count,
                    'avg_readability_index': avg_readability_index
                }
            else:
                print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
                print(
                    Fore.GREEN + Style.BRIGHT + '      СРЕДНИЕ ПОКАЗАТЕЛИ ' +
                    Fore.LIGHTGREEN_EX + Style.BRIGHT + 'ОСТАЛЬНЫХ ИНДИКАТОРОВ')
                print(Fore.LIGHTWHITE_EX + "*" * 80)

                table = Table()
                table.add_column("Показатель", justify="left", style="bold")
                table.add_column("Значение", justify="center", min_width=15)

                table.add_row("Отношение пассивных глаголов\nко всем глаголам (%)",
                              f"{avg_passive_to_all_v_ratio:.3f}%")
                table.add_row("Пассивные глаголы", f"{avg_passive_verbs_count:.2f}")
                table.add_row("Все глаголы", f"{avg_all_verbs_count:.2f}")
                table.add_row("\nИндекс читаемости по Флешу", f"\n{avg_readability_index:.3f}")

                console.print(table)
                wait_for_enter_to_analyze()

        self.cursor.execute('''
            SELECT func_words_freq, 
                   func_words_counts,
                   punct_marks_normalized_frequency, 
                   punct_marks_to_all_punct_frequency,
                   punctuation_counts,
                   pers_possessive_pronouns_frequencies,
                   pers_possessive_pronouns_counts,
                   reflexive_pronoun_frequencies, 
                   reflexive_pronoun_counts,
                   demonstrative_pronouns_frequencies, 
                   demonstrative_pronouns_counts,
                   defining_pronouns_frequencies, 
                   defining_pronouns_counts,
                   relative_pronouns_frequencies,
                   relative_pronouns_counts,
                   indefinite_pronouns_frequencies,
                   indefinite_pronouns_counts,
                   negative_pronouns_frequencies,
                   negative_pronouns_counts,
                   alpha_tokens_count,
                   all_tokens_count
            FROM Miscellaneous_features
            JOIN Simplification_features ON Miscellaneous_features.text_id = Simplification_features.text_id
        ''')
        result_json = self.cursor.fetchall()

        if result_json:
            # Инициализация накопителей для взвешенных значений
            func_words_freq_weighted = defaultdict(float)
            func_words_counts_weighted = defaultdict(float)

            punct_normalized_weighted = defaultdict(float)
            punct_to_all_weighted = defaultdict(float)
            punctuation_counts_weighted = defaultdict(float)

            pronoun_freq_accum = {
                'pers_possessive': defaultdict(float),
                'reflexive': defaultdict(float),
                'demonstrative': defaultdict(float),
                'defining': defaultdict(float),
                'relative': defaultdict(float),
                'indefinite': defaultdict(float),
                'negative': defaultdict(float)
            }

            pronoun_counts_accum = {
                'pers_possessive': defaultdict(float),
                'reflexive': defaultdict(float),
                'demonstrative': defaultdict(float),
                'defining': defaultdict(float),
                'relative': defaultdict(float),
                'indefinite': defaultdict(float),
                'negative': defaultdict(float)
            }

            total_tokens_sum = 0
            total_tokens_sum_with_punct = 0
            # Проходим по каждому тексту
            for row in result_json:
                (func_words_freq_json, func_words_counts_json, punct_norm_json,
                 punct_to_all_json, punctuation_counts_json,
                 pers_possessive_pronouns_frequencies,
                 pers_possessive_pronouns_counts,
                 reflexive_pronoun_frequencies,
                 reflexive_pronoun_counts,
                 demonstrative_pronouns_frequencies,
                 demonstrative_pronouns_counts,
                 defining_pronouns_frequencies,
                 defining_pronouns_counts,
                 relative_pronouns_frequencies,
                 relative_pronouns_counts,
                 indefinite_pronouns_frequencies,
                 indefinite_pronouns_counts,
                 negative_pronouns_frequencies,
                 negative_pronouns_counts,
                 alpha_tokens_count,
                 all_tokens_count) = row

                total_tokens_sum += alpha_tokens_count  # Суммируем количество токенов
                total_tokens_sum_with_punct += all_tokens_count

                # Обрабатываем JSON-поля
                func_words_freq = json.loads(func_words_freq_json)
                func_words_counts = json.loads(func_words_counts_json)
                punct_marks_normalized_frequency = json.loads(punct_norm_json)
                punct_marks_to_all_punct_frequency = json.loads(punct_to_all_json)
                punctuation_counts = json.loads(punctuation_counts_json)
                pers_possessive_pronouns_frequencies = json.loads(pers_possessive_pronouns_frequencies)
                pers_possessive_pronouns_counts = json.loads(pers_possessive_pronouns_counts)

                reflexive_pronoun_frequencies = json.loads(reflexive_pronoun_frequencies)
                reflexive_pronoun_counts = json.loads(reflexive_pronoun_counts)

                demonstrative_pronouns_frequencies = json.loads(demonstrative_pronouns_frequencies)
                demonstrative_pronouns_counts = json.loads(demonstrative_pronouns_counts)

                defining_pronouns_frequencies = json.loads(defining_pronouns_frequencies)
                defining_pronouns_counts = json.loads(defining_pronouns_counts)

                relative_pronouns_frequencies = json.loads(relative_pronouns_frequencies)
                relative_pronouns_counts = json.loads(relative_pronouns_counts)

                indefinite_pronouns_frequencies = json.loads(indefinite_pronouns_frequencies)
                indefinite_pronouns_counts = json.loads(indefinite_pronouns_counts)

                negative_pronouns_frequencies = json.loads(negative_pronouns_frequencies)
                negative_pronouns_counts = json.loads(negative_pronouns_counts)

                # Акумулирование данных с учетом количества токенов
                for word, freq in func_words_freq.items():
                    func_words_freq_weighted[word] += freq * alpha_tokens_count

                for word, count in func_words_counts.items():
                    func_words_counts_weighted[word] += count * alpha_tokens_count

                for punct, freq in punct_marks_normalized_frequency.items():
                    punct_normalized_weighted[punct] += freq * all_tokens_count

                for punct, freq in punct_marks_to_all_punct_frequency.items():
                    punct_to_all_weighted[punct] += freq * all_tokens_count

                for punct, count in punctuation_counts.items():
                    punctuation_counts_weighted[punct] += count * all_tokens_count

                for pronoun, freq in pers_possessive_pronouns_frequencies.items():
                    pronoun_freq_accum['pers_possessive'][pronoun] += freq * alpha_tokens_count

                for pronoun, count in pers_possessive_pronouns_counts.items():
                    pronoun_counts_accum['pers_possessive'][pronoun] += count * alpha_tokens_count

                for pronoun, freq in reflexive_pronoun_frequencies.items():
                    pronoun_freq_accum['reflexive'][pronoun] += freq * alpha_tokens_count

                for pronoun, count in reflexive_pronoun_counts.items():
                    pronoun_counts_accum['reflexive'][pronoun] += count * alpha_tokens_count

                for pronoun, freq in demonstrative_pronouns_frequencies.items():
                    pronoun_freq_accum['demonstrative'][pronoun] += freq * alpha_tokens_count

                for pronoun, count in demonstrative_pronouns_counts.items():
                    pronoun_counts_accum['demonstrative'][pronoun] += count * alpha_tokens_count

                for pronoun, freq in defining_pronouns_frequencies.items():
                    pronoun_freq_accum['defining'][pronoun] += freq * alpha_tokens_count

                for pronoun, count in defining_pronouns_counts.items():
                    pronoun_counts_accum['defining'][pronoun] += count * alpha_tokens_count

                for pronoun, freq in relative_pronouns_frequencies.items():
                    pronoun_freq_accum['relative'][pronoun] += freq * alpha_tokens_count

                for pronoun, count in relative_pronouns_counts.items():
                    pronoun_counts_accum['relative'][pronoun] += count * alpha_tokens_count

                for pronoun, freq in indefinite_pronouns_frequencies.items():
                    pronoun_freq_accum['indefinite'][pronoun] += freq * alpha_tokens_count

                for pronoun, count in indefinite_pronouns_counts.items():
                    pronoun_counts_accum['indefinite'][pronoun] += count * alpha_tokens_count

                for pronoun, freq in negative_pronouns_frequencies.items():
                    pronoun_freq_accum['negative'][pronoun] += freq * alpha_tokens_count

                for pronoun, count in negative_pronouns_counts.items():
                    pronoun_counts_accum['negative'][pronoun] += count * alpha_tokens_count

                # Вычисление взвешенных средних для всех частот и количеств
            avg_func_words_freq = {word: freq / total_tokens_sum for word, freq in func_words_freq_weighted.items()}
            avg_func_words_counts = {word: count / total_tokens_sum for word, count in
                                     func_words_counts_weighted.items()}

            avg_punct_normalized_frequency = {punct: freq / total_tokens_sum_with_punct for punct, freq in
                                              punct_normalized_weighted.items()}
            avg_punct_to_all_punct_frequency = {punct: freq / total_tokens_sum_with_punct for punct, freq in
                                                punct_to_all_weighted.items()}
            avg_punctuation_counts = {punct: count / total_tokens_sum_with_punct for punct, count in
                                      punctuation_counts_weighted.items()}

            avg_pers_possessive_pronouns_frequencies = {pronoun: freq / total_tokens_sum for pronoun, freq in
                                                        pronoun_freq_accum['pers_possessive'].items()}
            avg_pers_possessive_pronouns_counts = {pronoun: count / total_tokens_sum for pronoun, count in
                                                   pronoun_counts_accum['pers_possessive'].items()}

            avg_reflexive_pronoun_frequencies = {pronoun: freq / total_tokens_sum for pronoun, freq in
                                                 pronoun_freq_accum['reflexive'].items()}
            avg_reflexive_pronoun_counts = {pronoun: count / total_tokens_sum for pronoun, count in
                                            pronoun_counts_accum['reflexive'].items()}

            avg_demonstrative_pronouns_frequencies = {pronoun: freq / total_tokens_sum for pronoun, freq in
                                                      pronoun_freq_accum['demonstrative'].items()}
            avg_demonstrative_pronouns_counts = {pronoun: count / total_tokens_sum for pronoun, count in
                                                 pronoun_counts_accum['demonstrative'].items()}

            avg_defining_pronouns_frequencies = {pronoun: freq / total_tokens_sum for pronoun, freq in
                                                 pronoun_freq_accum['defining'].items()}
            avg_defining_pronouns_counts = {pronoun: count / total_tokens_sum for pronoun, count in
                                            pronoun_counts_accum['defining'].items()}

            avg_relative_pronouns_frequencies = {pronoun: freq / total_tokens_sum for pronoun, freq in
                                                 pronoun_freq_accum['relative'].items()}
            avg_relative_pronouns_counts = {pronoun: count / total_tokens_sum for pronoun, count in
                                            pronoun_counts_accum['relative'].items()}

            avg_indefinite_pronouns_frequencies = {pronoun: freq / total_tokens_sum for pronoun, freq in
                                                   pronoun_freq_accum['indefinite'].items()}
            avg_indefinite_pronouns_counts = {pronoun: count / total_tokens_sum for pronoun, count in
                                              pronoun_counts_accum['indefinite'].items()}

            avg_negative_pronouns_frequencies = {pronoun: freq / total_tokens_sum for pronoun, freq in
                                                 pronoun_freq_accum['negative'].items()}
            avg_negative_pronouns_counts = {pronoun: count / total_tokens_sum for pronoun, count in
                                            pronoun_counts_accum['negative'].items()}

            if comparison:
                comparison_results[self.db_name].update({
                    'avg_func_words_freq': avg_func_words_freq,
                    'avg_punct_normalized_frequency': avg_punct_normalized_frequency,
                    'avg_punct_to_all_punct_frequency': avg_punct_to_all_punct_frequency,
                    'avg_pers_possessive_pronouns_frequencies': avg_pers_possessive_pronouns_frequencies,
                    'avg_reflexive_pronoun_frequencies': avg_reflexive_pronoun_frequencies,
                    'avg_demonstrative_pronouns_frequencies': avg_demonstrative_pronouns_frequencies,
                    'avg_defining_pronouns_frequencies': avg_defining_pronouns_frequencies,
                    'avg_relative_pronouns_frequencies': avg_relative_pronouns_frequencies,
                    'avg_indefinite_pronouns_frequencies': avg_indefinite_pronouns_frequencies,
                    'avg_negative_pronouns_frequencies': avg_negative_pronouns_frequencies,
                })

            else:

                print(Fore.GREEN + Style.BRIGHT + '\n                 СРЕДНИЕ ЧАСТОТЫ СЛУЖЕБНЫХ СЛОВ')
                wait_for_enter_to_analyze()
                table_func_words = Table()
                table_func_words.add_column("Слово\n", justify="left")
                table_func_words.add_column("Абсолютная частота\n", justify="center")
                table_func_words.add_column("Нормализованная частота\n(%)", justify="center")

                for word, freq in sorted(avg_func_words_freq.items(), key=lambda item: item[1], reverse=True):
                    count = avg_func_words_counts.get(word, 0)
                    table_func_words.add_row(word, f"{count:.3f}", f"{freq:.3f}%")

                console.print(table_func_words)
                wait_for_enter_to_analyze()

                def show_average_pronouns_info(pronouns_type, pronouns_freq, pronouns_count):
                    pro_name = ''
                    if pronouns_type == 'pers_possessive':
                        pro_name = 'ЛИЧНЫХ И ПРИТЯЖАТЕЛЬНЫХ'
                    elif pronouns_type == 'reflexive_pronoun':
                        pro_name = 'ВОЗВРАТНЫХ'
                    elif pronouns_type == 'demonstrative_pronouns':
                        pro_name = 'УКАЗАТЕЛЬНЫХ'
                    elif pronouns_type == 'defining_pronouns':
                        pro_name = 'ОПРЕДЕЛИТЕЛЬНЫХ'
                    elif pronouns_type == 'relative_pronouns':
                        pro_name = 'ОТНОСИТЕЛЬНЫХ'
                    elif pronouns_type == 'indefinite_pronouns':
                        pro_name = 'НЕОПРЕДЕЛЕННЫХ'
                    elif pronouns_type == 'negative_pronouns':
                        pro_name = 'ОТРИЦАТЕЛЬНЫХ'

                    print(Fore.GREEN + Style.BRIGHT + f'\n              СРЕДНИЕ ЧАСТОТЫ {pro_name} МЕСТОИМЕНИЙ')
                    table_pronouns = Table()
                    table_pronouns.add_column("Местоимение\n", justify="center")
                    table_pronouns.add_column("Абсолютная частота\n", justify="center")
                    table_pronouns.add_column("Нормализованная частота\n(%)", justify="center")

                    for pronoun, freq in sorted(pronouns_freq.items(), key=lambda item: item[1], reverse=True):
                        count = pronouns_count.get(pronoun, 0)
                        table_pronouns.add_row(pronoun, f'{count:.3f}', f"{freq:.3f}%")

                    console.print(table_pronouns)

                show_average_pronouns_info('pers_possessive', avg_pers_possessive_pronouns_frequencies,
                                           avg_pers_possessive_pronouns_counts)
                wait_for_enter_to_analyze()

                show_average_pronouns_info('reflexive_pronoun', avg_reflexive_pronoun_frequencies,
                                           avg_reflexive_pronoun_counts)
                wait_for_enter_to_analyze()

                show_average_pronouns_info('demonstrative_pronouns', avg_demonstrative_pronouns_frequencies,
                                           avg_demonstrative_pronouns_counts)
                wait_for_enter_to_analyze()

                show_average_pronouns_info('defining_pronouns', avg_defining_pronouns_frequencies,
                                           avg_defining_pronouns_counts)
                wait_for_enter_to_analyze()

                show_average_pronouns_info('relative_pronouns', avg_relative_pronouns_frequencies,
                                           avg_relative_pronouns_counts)
                wait_for_enter_to_analyze()

                show_average_pronouns_info('indefinite_pronouns', avg_indefinite_pronouns_frequencies,
                                           avg_indefinite_pronouns_counts)
                wait_for_enter_to_analyze()

                show_average_pronouns_info('negative_pronouns', avg_negative_pronouns_frequencies,
                                           avg_negative_pronouns_counts)

                wait_for_enter_to_analyze()

                print(
                    Fore.GREEN + Style.BRIGHT + '\n                       СРЕДНИЕ ЧАСТОТЫ ЗНАКОВ ПРЕПИНАНИЯ')
                table_punctuation = Table()
                table_punctuation.add_column("Знак\n", justify="center")
                table_punctuation.add_column("Абсолютная частота\n", justify="center")
                table_punctuation.add_column("Частота ко всем\nтокенам текста (%)", justify="center")
                table_punctuation.add_column("Частота ко всем\nзнакам препинания (%)", justify="center")

                for punct in sorted(avg_punct_normalized_frequency.keys(),
                                    key=lambda item: avg_punct_normalized_frequency[item], reverse=True):
                    count = avg_punctuation_counts.get(punct, 0)
                    norm_freq = avg_punct_normalized_frequency.get(punct, 0)
                    all_punct_freq = avg_punct_to_all_punct_frequency.get(punct, 0)

                    if norm_freq > 0 or all_punct_freq > 0:
                        table_punctuation.add_row(punct, f"{count:.2f}", f"{norm_freq:.2f}%", f"{all_punct_freq:.2f}%")

                console.print(table_punctuation)
                wait_for_enter_to_analyze()

        else:
            print("Нет данных для отображения.")

    def display_interference_features_for_corpus(self, comparison=False, comparison_results=None):
        """Отображает средние показатели для индикаторов универсалии Interference."""
        self.cursor.execute('''
            SELECT 
                Interference_features.pos_unigrams_counts, 
                Interference_features.pos_unigrams_freq, 
                Interference_features.pos_bigrams_counts, 
                Interference_features.pos_bigrams_freq, 
                Interference_features.pos_trigrams_counts, 
                Interference_features.pos_trigrams_freq, 
                Interference_features.char_unigram_counts, 
                Interference_features.char_unigram_freq, 
                Interference_features.char_bigram_counts, 
                Interference_features.char_bigram_freq, 
                Interference_features.char_trigram_counts, 
                Interference_features.char_trigram_freq, 
                Interference_features.func_w_trigrams_freqs, 
                Interference_features.func_w_trigram_with_pos_counts, 
                Interference_features.token_positions_normalized_frequencies, 
                Interference_features.token_positions_counts, 
                Simplification_features.all_tokens_count
            FROM Interference_features
            JOIN Simplification_features ON Interference_features.text_id = Simplification_features.text_id
        ''')
        rows = self.cursor.fetchall()

        if not rows:
            print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "Нет данных для отображения." + Fore.RESET)
            return

        # Инициализация аккумуляторов для всех данных
        counts_totals = {
            'pos_unigrams': defaultdict(int),
            'pos_bigrams': defaultdict(int),
            'pos_trigrams': defaultdict(int),
            'char_unigrams': defaultdict(int),
            'char_bigrams': defaultdict(int),
            'char_trigrams': defaultdict(int),
            'func_w_trigrams': defaultdict(lambda: defaultdict(int)),
            'token_positions': defaultdict(lambda: defaultdict(int)),
        }

        freqs_totals = {
            'pos_unigrams': defaultdict(float),
            'pos_bigrams': defaultdict(float),
            'pos_trigrams': defaultdict(float),
            'char_unigrams': defaultdict(float),
            'char_bigrams': defaultdict(float),
            'char_trigrams': defaultdict(float),
            'func_w_trigrams': defaultdict(lambda: defaultdict(float)),
            'token_positions': defaultdict(lambda: defaultdict(float)),
        }
        total_tokens_sum = 0  # Общая сумма токенов для вычисления взвешенных средних

        # Проходим по каждому ряду (тексту)
        for row in rows:
            total_tokens = row[16]  # Общее количество токенов в тексте из Simplification_features!!!
            total_tokens_sum += total_tokens  # Акумулируем общее количество токенов для всех текстов

            # Десериализация POS n-граммов
            pos_unigrams_counts = json.loads(row[0])
            pos_unigrams_freq = json.loads(row[1])
            pos_bigrams_counts = json.loads(row[2])
            pos_bigrams_freq = json.loads(row[3])
            pos_trigrams_counts = json.loads(row[4])
            pos_trigrams_freq = json.loads(row[5])

            # Десериализация char n-граммов
            char_unigrams_counts = json.loads(row[6])
            char_unigrams_freq = json.loads(row[7])
            char_bigrams_counts = json.loads(row[8])
            char_bigrams_freq = json.loads(row[9])
            char_trigrams_counts = json.loads(row[10])
            char_trigrams_freq = json.loads(row[11])

            # Десериализация функциональных триграмм
            func_w_trigrams_freqs = json.loads(row[12])
            func_w_trigram_with_pos_counts = json.loads(row[13])

            # Десериализация позиционных данных
            token_positions_normalized_frequencies = json.loads(row[14])
            token_positions_counts = json.loads(row[15])

            # Акумулирование данных для POS n-граммов (взвешенные средние)
            for key, count in pos_unigrams_counts.items():
                counts_totals['pos_unigrams'][key] += count * total_tokens
            for key, freq in pos_unigrams_freq.items():
                freqs_totals['pos_unigrams'][key] += (freq * total_tokens)

            for key, count in pos_bigrams_counts.items():
                counts_totals['pos_bigrams'][key] += count * total_tokens
            for key, freq in pos_bigrams_freq.items():
                freqs_totals['pos_bigrams'][key] += freq * total_tokens

            for key, count in pos_trigrams_counts.items():
                counts_totals['pos_trigrams'][key] += count * total_tokens
            for key, freq in pos_trigrams_freq.items():
                freqs_totals['pos_trigrams'][key] += freq * total_tokens

            # Акумулирование данных для char n-граммов
            for key, count in char_unigrams_counts.items():
                counts_totals['char_unigrams'][key] += count * total_tokens
            for key, freq in char_unigrams_freq.items():
                freqs_totals['char_unigrams'][key] += freq * total_tokens

            for key, count in char_bigrams_counts.items():
                counts_totals['char_bigrams'][key] += count * total_tokens
            for key, freq in char_bigrams_freq.items():
                freqs_totals['char_bigrams'][key] += freq * total_tokens

            for key, count in char_trigrams_counts.items():
                counts_totals['char_trigrams'][key] += count * total_tokens
            for key, freq in char_trigrams_freq.items():
                freqs_totals['char_trigrams'][key] += freq * total_tokens

            # Акумулирование данных для функциональных триграмм
            for category, trigrams in func_w_trigrams_freqs.items():
                for trigram, freq in trigrams.items():
                    freqs_totals['func_w_trigrams'][category][trigram] += freq * total_tokens

            for category, trigrams in func_w_trigram_with_pos_counts.items():
                for trigram, count in trigrams.items():
                    counts_totals['func_w_trigrams'][category][trigram] += count * total_tokens

            # Акумулирование данных для позиционных токенов
            for position, tokens in token_positions_normalized_frequencies.items():
                for token, freq in tokens.items():
                    freqs_totals['token_positions'][position][token] += freq * total_tokens

            for position, tokens in token_positions_counts.items():
                for token, count in tokens.items():
                    counts_totals['token_positions'][position][token] += count * total_tokens
            # Добавляем данные в comparison_results для текущего корпуса
            if comparison:
                comparison_results[self.db_name] = {
                    'pos_unigrams_freq': {key: freq / total_tokens_sum for key, freq in
                                          freqs_totals['pos_unigrams'].items()},
                    'pos_bigrams_freq': {key: freq / total_tokens_sum for key, freq in
                                         freqs_totals['pos_bigrams'].items()},
                    'pos_trigrams_freq': {key: freq / total_tokens_sum for key, freq in
                                          freqs_totals['pos_trigrams'].items()},
                    'char_unigrams_freq': {key: freq / total_tokens_sum for key, freq in
                                           freqs_totals['char_unigrams'].items()},
                    'char_bigrams_freq': {key: freq / total_tokens_sum for key, freq in
                                          freqs_totals['char_bigrams'].items()},
                    'char_trigrams_freq': {key: freq / total_tokens_sum for key, freq in
                                           freqs_totals['char_trigrams'].items()},
                    'func_w_trigrams_freqs': {
                        category: {trigram: freq / total_tokens_sum for trigram, freq in trigrams.items()} for
                        category, trigrams in freqs_totals['func_w_trigrams'].items()},
                    'token_positions_normalized_frequencies': {
                        position: {token: freq / total_tokens_sum for token, freq in tokens.items()} for
                        position, tokens in freqs_totals['token_positions'].items()},
                }

        # Функция для создания таблиц с результатами
        def create_table(counts_dict, freq_dict, total_tokens_sum, min_count):
            table = Table()
            table.add_column("N-gram", style="bold", justify="center", max_width=40)
            table.add_column("Количество", justify="center")
            table.add_column("Взвешенная частота", justify="center")

            sorted_ngrams = []

            # Проходим по всем n-граммам и проверяем их средние значения
            for key in counts_dict:
                total_count = counts_dict[key]
                average_count = total_count / total_tokens_sum  # Среднее количество n-граммов с учетом токенов

                # Проверяем, что значение превышает заданный min_count
                if average_count >= min_count:
                    weighted_freq = freq_dict.get(key, 0)
                    average_freq = weighted_freq / total_tokens_sum  # Взвешенная частота
                    sorted_ngrams.append((key, average_count, average_freq))

            # Сортируем n-граммы по частоте и количеству
            sorted_ngrams.sort(key=lambda x: (-x[2], -x[1]))

            # Добавляем строки в таблицу
            for ngram, avg_count, avg_freq in sorted_ngrams:
                table.add_row(ngram, f"{avg_count:.3f}", f"{avg_freq:.3f}")

            return table

        if not comparison:
            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.GREEN + Style.BRIGHT + '\n              СРЕДНИЕ ПОКАЗАТЕЛИ ХАРАКТЕРИСТИКИ' + Fore.LIGHTGREEN_EX +
                Style.BRIGHT + ' INTERFERENCE')
            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)

            display_grammemes()
            wait_for_enter_to_analyze()

        def min_count_choice():
            while True:
                try:
                    min_count_input = input(Fore.LIGHTGREEN_EX + Style.BRIGHT +
                                            f"Введите минимальное значение для среднего количества выводимых n-граммов"
                                            f"\nили просто нажмите 'Enter', чтобы продолжить "
                                            f"(по умолчанию значение=1): \n").strip()

                    if not min_count_input:
                        min_count = 1
                        break
                    else:
                        min_count = float(min_count_input)
                        break
                except ValueError:
                    print(Fore.LIGHTRED_EX + Style.BRIGHT + "\nОшибка! Введите числовое значение." + Fore.RESET)
            return min_count

        if not comparison:
            min_count = min_count_choice()
            print(
                Fore.GREEN + Style.BRIGHT + "\nСРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ" + Fore.LIGHTGREEN_EX + Style.BRIGHT
                + " UNIGRAMS" + Fore.GREEN + Style.BRIGHT + " В КОРПУСЕ" + Fore.RESET)
            wait_for_enter_to_analyze()
            pos_unigram_table = create_table(counts_totals['pos_unigrams'], freqs_totals['pos_unigrams'],
                                             total_tokens_sum, min_count)
            console.print(pos_unigram_table)
            wait_for_enter_to_analyze()

            print(
                Fore.GREEN + Style.BRIGHT + "СРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ" + Fore.LIGHTGREEN_EX + Style.BRIGHT
                + " BIGRAMS" + Fore.GREEN + Style.BRIGHT + " В КОРПУСЕ" + Fore.RESET)
            wait_for_enter_to_analyze()
            pos_bigram_table = create_table(counts_totals['pos_bigrams'], freqs_totals['pos_bigrams'],
                                            total_tokens_sum, min_count)
            console.print(pos_bigram_table)
            wait_for_enter_to_analyze()

            print(
                Fore.GREEN + Style.BRIGHT + "СРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ" + Fore.LIGHTGREEN_EX + Style.BRIGHT
                + " TRIGRAMS" + Fore.GREEN + Style.BRIGHT + " В КОРПУСЕ" + Fore.RESET)
            wait_for_enter_to_analyze()
            pos_trigram_table = create_table(counts_totals['pos_trigrams'], freqs_totals['pos_trigrams'],
                                             total_tokens_sum, min_count)
            console.print(pos_trigram_table)
            wait_for_enter_to_analyze()

            print(
                Fore.GREEN + Style.BRIGHT + "\n            ДАЛЕЕ БУДЕТ ПОКАЗАН АНАЛИЗ БУКВЕННЫХ N-ГРАММОВ" + Fore.RESET)
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Внимание! N-граммы '<' и '>' используются для обозначания начала и конца "
                                                  "\nслов соответственно.\n" + Fore.RESET)
            wait_for_enter_to_analyze()
            min_count = min_count_choice()

            print(
                Fore.GREEN + Style.BRIGHT + "\nСРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ" + Fore.LIGHTGREEN_EX + Style.BRIGHT +
                " UNIGRAMS" + Fore.GREEN + Style.BRIGHT + " В КОРПУСЕ" + Fore.RESET)
            wait_for_enter_to_analyze()
            char_unigram_table = create_table(counts_totals['char_unigrams'], freqs_totals['char_unigrams'],
                                              total_tokens_sum, min_count)
            console.print(char_unigram_table)
            wait_for_enter_to_analyze()

            print(
                Fore.GREEN + Style.BRIGHT + "СРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ" + Fore.LIGHTGREEN_EX + Style.BRIGHT +
                " BIGRAMS" + Fore.GREEN + Style.BRIGHT + " В КОРПУСЕ" + Fore.RESET)
            wait_for_enter_to_analyze()
            char_bigram_table = create_table(counts_totals['char_bigrams'], freqs_totals['char_bigrams'],
                                             total_tokens_sum, min_count)
            console.print(char_bigram_table)
            wait_for_enter_to_analyze()

            print(
                Fore.GREEN + Style.BRIGHT + "СРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ" + Fore.LIGHTGREEN_EX + Style.BRIGHT +
                " TRIGRAMS" + Fore.GREEN + Style.BRIGHT + " В КОРПУСЕ" + Fore.RESET)
            wait_for_enter_to_analyze()
            char_trigram_table = create_table(counts_totals['char_trigrams'], freqs_totals['char_trigrams'],
                                              total_tokens_sum, min_count)
            console.print(char_trigram_table)
            wait_for_enter_to_analyze()

        def min_count_choice_for_posiitions():
            while True:
                try:
                    min_count_input = input(Fore.LIGHTGREEN_EX + Style.BRIGHT +
                                            f"Введите минимальное значение для среднего количества выводимых токенов"
                                            f"\nна той или иной позиции или просто нажмите 'Enter', чтобы продолжить"
                                            f"\n(по умолчанию значение=1): \n").strip()

                    if not min_count_input:
                        min_count = 1
                        break
                    else:
                        min_count = float(min_count_input)
                        break
                except ValueError:
                    print(Fore.LIGHTRED_EX + Style.BRIGHT + "\nОшибка! Введите числовое значение." + Fore.RESET)
            return min_count

        if not comparison:
            print(
                Fore.GREEN + Style.BRIGHT + f"\nДАЛЕЕ БУДУТ ВЫВЕДЕНЫ СРЕДНИЕ ПОЗИЦИОННЫЕ ПОКАЗАТЕЛИ ТОКЕНОВ В ТЕКСТЕ" + Fore.RESET)
            display_position_explanation()
            min_count = min_count_choice_for_posiitions()
            for position in ['first', 'second', 'antepenultimate', 'penultimate', 'last']:
                print(
                    Fore.GREEN + Style.BRIGHT + f"\n* Средние показатели для позиций:" + Fore.LIGHTGREEN_EX + Style.BRIGHT + f" {position.upper()}" + Fore.RESET)
                wait_for_enter_to_analyze()
                # Создаем таблицу для каждой позиции с учетом min_count
                token_count_table = create_table(
                    counts_totals['token_positions'][position],  # Словарь с количествами токенов для позиции
                    freqs_totals['token_positions'][position],  # Словарь с нормализованными частотами для позиции
                    total_tokens_sum,  # Общее количество токенов (вес)
                    min_count  # Минимальное значение для фильтрации
                )
                console.print(token_count_table)
                wait_for_enter_to_analyze()
        if not comparison:
            print(
                Fore.GREEN + Style.BRIGHT + "\nСРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ ТРИГРАММОВ С 1,2,3 ФУНКЦИОНАЛЬНЫМИ СЛОВАМИ\n" + Fore.RESET)
            min_count = min_count_choice()
            for category in counts_totals['func_w_trigrams']:
                print(
                    Fore.GREEN + Style.BRIGHT + f"\n                  {category.upper()}" + Fore.RESET)
                wait_for_enter_to_analyze()
                func_trigram_table = create_table(counts_totals['func_w_trigrams'][category],
                                                  freqs_totals['func_w_trigrams'][category], total_tokens_sum,
                                                  min_count)

                console.print(func_trigram_table)
                wait_for_enter_to_choose_opt()

    def delete_text_from_corpus(self, text_id):
        """Удаляет записи о тексте по text_id из всех таблиц."""
        self.cursor.execute("DELETE FROM Text_Passport WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Simplification_features WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Normalisation_features WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Explicitation_features WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Interference_features WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Miscellaneous_features WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Morphological_annotation WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Syntactic_annotation WHERE text_id = ?", (text_id,))

        self.connection.commit()

        print(
            Fore.LIGHTGREEN_EX + Style.BRIGHT + f"Запись о тексте выбранном тексте и все связанные с ним данные были успешно удалены!\n" + Fore.RESET)

    def print_simpl_comparison_table(self, comparison_results):
        """Выводит сравнительную таблицу для разных баз данных"""
        print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
        print(
            Fore.GREEN + Style.BRIGHT + '             СРАВНЕНИЕ ПОКАЗАТЕЛЕЙ ' + Fore.LIGHTGREEN_EX + Style.BRIGHT
            + 'SIMPLIFICATION' + Fore.GREEN + Style.BRIGHT + ' ПО КОРПУСАМ' + Fore.LIGHTRED_EX + Style.BRIGHT)
        print(Fore.LIGHTWHITE_EX + "*" * 80)
        table = Table()

        table.add_column("Показатель", justify="left", style="bold")
        for db in comparison_results.keys():
            table.add_column(db, justify="center", style="bold")

        for feature in comparison_results[list(comparison_results.keys())[0]].keys():
            row = [feature]
            for db in comparison_results.keys():
                row.append(f"{comparison_results[db][feature]:.2f}")
            table.add_row(*row)

        console.print(table)
        print(Fore.LIGHTWHITE_EX + "*" * 80)
        wait_for_enter_to_choose_opt()

    def print_ngrams_comparison_table(self, comparison_results):
        """Печатает таблицу сравнения частот n-граммов для разных корпусов"""
        print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
        print(
            Fore.GREEN + Style.BRIGHT + '             СРАВНЕНИЕ ПОКАЗАТЕЛЕЙ ' + Fore.LIGHTGREEN_EX + Style.BRIGHT
            + 'ЧАСТЕРЕЧНЫХ УНИГРАММ' + Fore.GREEN + Style.BRIGHT + ' ПО КОРПУСАМ' + Fore.LIGHTRED_EX + Style.BRIGHT)
        print(Fore.LIGHTWHITE_EX + "*" * 80)
        table = Table()
        # Создание таблицы для POS Unigrams
        table.add_column("Unigram", justify="left", style="bold")
        for db in comparison_results.keys():
            table.add_column(db, justify="center", style="bold")

        all_pos = set()
        for corpus_data in comparison_results.values():
            all_pos.update(corpus_data.get('pos_unigrams_freq', {}).keys())

        sorted_pos = sorted(all_pos, key=lambda x: comparison_results[list(comparison_results.keys())[0]].get(
            'pos_unigrams_freq', {}).get(x, 0), reverse=True)

        for pos in sorted_pos:
            row = [pos]
            for corpus_name, corpus_data in comparison_results.items():
                freq = corpus_data.get('pos_unigrams_freq', {}).get(pos, 0)
                row.append(f"{round(freq, 4)}")
            table.add_row(*row)

        console.print(table)
        wait_for_enter_to_analyze()

        print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
        print(
            Fore.GREEN + Style.BRIGHT + '             СРАВНЕНИЕ ПОКАЗАТЕЛЕЙ ' + Fore.LIGHTGREEN_EX + Style.BRIGHT
            + 'ЧАСТЕРЕЧНЫХ БИГРАММ' + Fore.GREEN + Style.BRIGHT + ' ПО КОРПУСАМ' + Fore.LIGHTRED_EX + Style.BRIGHT)
        print(Fore.LIGHTWHITE_EX + "*" * 80)
        table = Table()
        table.add_column("Bigrams", justify="left", style="bold")
        for db in comparison_results.keys():
            table.add_column(db, justify="center", style="bold")

        all_bigrams = set()
        for corpus_data in comparison_results.values():
            all_bigrams.update(corpus_data.get('pos_bigrams_freq', {}).keys())

        sorted_bigrams = sorted(all_bigrams, key=lambda x: comparison_results[list(comparison_results.keys())[0]].get(
            'pos_bigrams_freq', {}).get(x, 0), reverse=True)

        for bigram in sorted_bigrams:
            row = [bigram]
            for corpus_name, corpus_data in comparison_results.items():
                freq = corpus_data.get('pos_bigrams_freq', {}).get(bigram, 0)
                row.append(f"{round(freq, 4)}")
            table.add_row(*row)

        console.print(table)
        wait_for_enter_to_analyze()

        print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
        print(
            Fore.GREEN + Style.BRIGHT + '             СРАВНЕНИЕ ПОКАЗАТЕЛЕЙ ' + Fore.LIGHTGREEN_EX + Style.BRIGHT
            + 'ЧАСТЕРЕЧНЫХ ТРИГРАММ' + Fore.GREEN + Style.BRIGHT + ' ПО КОРПУСАМ' + Fore.LIGHTRED_EX + Style.BRIGHT)
        print(Fore.LIGHTWHITE_EX + "*" * 80)
        table = Table()
        table.add_column("Trigrams", justify="left", style="bold")
        for db in comparison_results.keys():
            table.add_column(db, justify="center", style="bold")

        all_trigrams = set()
        for corpus_data in comparison_results.values():
            all_trigrams.update(corpus_data.get('pos_trigrams_freq', {}).keys())

        sorted_trigrams = sorted(all_trigrams, key=lambda x: comparison_results[list(comparison_results.keys())[0]].get(
            'pos_trigrams_freq', {}).get(x, 0), reverse=True)

        for trigram in sorted_trigrams:
            row = [trigram]
            for corpus_name, corpus_data in comparison_results.items():
                freq = corpus_data.get('pos_trigrams_freq', {}).get(trigram, 0)
                row.append(f"{round(freq, 4)}")
            table.add_row(*row)

        console.print(table)
        wait_for_enter_to_analyze()

        print(
            Fore.GREEN + Style.BRIGHT + '             СРАВНЕНИЕ ПОКАЗАТЕЛЕЙ ' + Fore.LIGHTGREEN_EX + Style.BRIGHT
            + 'СИМВОЛЬНЫХ УНИГРАММ' + Fore.GREEN + Style.BRIGHT + ' ПО КОРПУСАМ' + Fore.LIGHTRED_EX + Style.BRIGHT)
        print(Fore.LIGHTWHITE_EX + "*" * 80)
        table = Table()
        table.add_column("Char Unigrams", justify="left", style="bold")
        for db in comparison_results.keys():
            table.add_column(db, justify="center", style="bold")

        all_char_unigrams = set()
        for corpus_data in comparison_results.values():
            all_char_unigrams.update(corpus_data.get('char_unigrams_freq', {}).keys())

        sorted_char_unigrams = sorted(all_char_unigrams,
                                      key=lambda x: comparison_results[list(comparison_results.keys())[0]].get(
                                          'char_unigrams_freq', {}).get(x, 0), reverse=True)

        for char_unigram in sorted_char_unigrams:
            row = [char_unigram]
            for corpus_name, corpus_data in comparison_results.items():
                freq = corpus_data.get('char_unigrams_freq', {}).get(char_unigram, 0)
                row.append(f"{round(freq, 4)}")
            table.add_row(*row)

        console.print(table)
        wait_for_enter_to_analyze()

        print(
            Fore.GREEN + Style.BRIGHT + '             СРАВНЕНИЕ ПОКАЗАТЕЛЕЙ ' + Fore.LIGHTGREEN_EX + Style.BRIGHT
            + 'СИМВОЛЬНЫХ БИГРАММ' + Fore.GREEN + Style.BRIGHT + ' ПО КОРПУСАМ' + Fore.LIGHTRED_EX + Style.BRIGHT)
        print(Fore.LIGHTWHITE_EX + "*" * 80)
        table = Table()
        table.add_column("Char Bigrams", justify="left", style="bold")
        for db in comparison_results.keys():
            table.add_column(db, justify="center", style="bold")

        all_char_bigrams = set()
        for corpus_data in comparison_results.values():
            all_char_bigrams.update(corpus_data.get('char_bigrams_freq', {}).keys())

        sorted_char_bigrams = sorted(all_char_bigrams,
                                     key=lambda x: comparison_results[list(comparison_results.keys())[0]].get(
                                         'char_bigrams_freq', {}).get(x, 0), reverse=True)

        for char_bigram in sorted_char_bigrams:
            row = [char_bigram]
            for corpus_name, corpus_data in comparison_results.items():
                freq = corpus_data.get('char_bigrams_freq', {}).get(char_bigram, 0)
                row.append(f"{round(freq, 4)}")
            table.add_row(*row)

        console.print(table)
        wait_for_enter_to_analyze()

        print(
            Fore.GREEN + Style.BRIGHT + '             СРАВНЕНИЕ ПОКАЗАТЕЛЕЙ ' + Fore.LIGHTGREEN_EX + Style.BRIGHT
            + 'СИМВОЛЬНЫХ ТРИГРАММ' + Fore.GREEN + Style.BRIGHT + ' ПО КОРПУСАМ' + Fore.LIGHTRED_EX + Style.BRIGHT)
        print(Fore.LIGHTWHITE_EX + "*" * 80)
        table = Table()
        table.add_column("Char Trigrams", justify="left", style="bold")
        for db in comparison_results.keys():
            table.add_column(db, justify="center", style="bold")

        all_char_trigrams = set()
        for corpus_data in comparison_results.values():
            all_char_trigrams.update(corpus_data.get('char_trigrams_freq', {}).keys())

        sorted_char_trigrams = sorted(all_char_trigrams,
                                      key=lambda x: comparison_results[list(comparison_results.keys())[0]].get(
                                          'char_trigrams_freq', {}).get(x, 0), reverse=True)

        for char_trigram in sorted_char_trigrams:
            row = [char_trigram]
            for corpus_name, corpus_data in comparison_results.items():
                freq = corpus_data.get('char_trigrams_freq', {}).get(char_trigram, 0)
                row.append(f"{round(freq, 4)}")
            table.add_row(*row)

        console.print(table)
        wait_for_enter_to_analyze()

        print(
            Fore.GREEN + Style.BRIGHT + '             СРАВНЕНИЕ ПОКАЗАТЕЛЕЙ ' + Fore.LIGHTGREEN_EX + Style.BRIGHT
            + 'ТРИГРАММ С ФУНКЦИОНАЛЬНЫМИ СЛОВАМИ' + Fore.GREEN + Style.BRIGHT + ' ПО КОРПУСАМ' + Fore.LIGHTRED_EX + Style.BRIGHT)
        print(Fore.LIGHTWHITE_EX + "*" * 80)
        table = Table()
        table.add_column("Functional Trigrams", justify="left", style="bold")
        for db in comparison_results.keys():
            table.add_column(db, justify="center", style="bold")

        all_func_w_trigrams = set()
        for corpus_data in comparison_results.values():
            for category, trigrams in corpus_data.get('func_w_trigrams_freqs', {}).items():
                all_func_w_trigrams.update(trigrams.keys())

        sorted_func_w_trigrams = sorted(all_func_w_trigrams, key=lambda x: next(iter(comparison_results.values())).get(
            'func_w_trigrams_freqs', {}).get(
            next(iter(next(iter(comparison_results.values())).get('func_w_trigrams_freqs', {})), {}), {}).get(x, 0),
                                        reverse=True)

        for func_w_trigram in sorted_func_w_trigrams:
            row = [str(func_w_trigram)]
            for corpus_name, corpus_data in comparison_results.items():
                freq = 0
                func_trigrams = corpus_data.get('func_w_trigrams_freqs', {})
                for category, trigrams in func_trigrams.items():
                    if func_w_trigram in trigrams:
                        freq = trigrams[func_w_trigram]
                        break
                row.append(f"{round(freq, 4)}")
            table.add_row(*row)

        console.print(table)
        wait_for_enter_to_analyze()

    def print_normalisation_comparison_table(self, comparison_results):
        """Выводит сравнительную таблицу нормализации для разных баз данных"""
        print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
        print(
            Fore.GREEN + Style.BRIGHT + '               СРАВНЕНИЕ ПОКАЗАТЕЛЕЙ ' + Fore.LIGHTGREEN_EX + Style.BRIGHT
            + 'NORMALISATION' + Fore.GREEN + Style.BRIGHT + ' ПО КОРПУСАМ' + Fore.LIGHTRED_EX + Style.BRIGHT)
        print(Fore.LIGHTWHITE_EX + "*" * 80)
        table = Table()

        table.add_column("Показатель", justify="left", style="bold")
        for db in comparison_results.keys():
            table.add_column(db, justify="center", style="bold")

        for feature in comparison_results[list(comparison_results.keys())[0]].keys():
            row = [feature]
            for db in comparison_results.keys():
                value = comparison_results[db][feature]
                if isinstance(value, float):
                    row.append(f"{value:.2f}")
                elif isinstance(value, int):
                    row.append(str(value))
                else:
                    row.append(str(value))
            table.add_row(*row)

        console.print(table)
        print(Fore.LIGHTWHITE_EX + "*" * 80)
        wait_for_enter_to_choose_opt()

    def print_explicitation_comparison_table(self, comparison_results):
        """Выводит сравнительную таблицу для показателей Explicitation по корпусам"""
        print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
        print(
            Fore.GREEN + Style.BRIGHT + '                 СРАВНЕНИЕ ПОКАЗАТЕЛЕЙ ' + Fore.LIGHTGREEN_EX + Style.BRIGHT
            + 'EXPLICITATION' + Fore.GREEN + Style.BRIGHT + ' ПО КОРПУСАМ' + Fore.LIGHTRED_EX + Style.BRIGHT)
        print(Fore.LIGHTWHITE_EX + "*" * 80)
        table = Table()

        # Добавляем колонки
        table.add_column("Показатель", justify="left", style="bold")
        for db in comparison_results.keys():
            table.add_column(db, justify="center", style="bold")

        # Создаем словарь с понятными названиями показателей
        feature_names = {
            'explicit_naming_ratio': 'Коэфф. явного называния',
            'single_naming': 'Коэфф единочного именования',
            'mean_multiple_naming': 'Средняя длина именованных сущностей',
            'named_entities_count': 'Количество именованных сущностей',
            'sci_markers_total_count': 'Общее количество дискурсивных маркеров',
            'topic_intro_dm_freq': 'Введение в тему',
            'info_sequence_freq': 'Порядок следования информации',
            'illustration_dm_freq': 'Иллюстративный материал',
            'material_sequence_freq': 'Порядок расположения материала',
            'conclusion_dm_freq': 'Вывод/заключение',
            'intro_new_addit_info_freq': 'Введение новой/доп. информации',
            'info_explanation_or_repetition_freq': 'Повтор/конкретизация информации',
            'contrast_dm_freq': 'Противопоставление',
            'examples_introduction_dm_freq': 'Введение примеров',
            'author_opinion_freq': 'Мнение автораа',
            'author_attitude_freq': 'Отношение автора',
            'high_certainty_modal_words_freq': 'Высокая степень уверенности',
            'moderate_certainty_modal_words_freq': 'Средняя степень уверенности',
            'uncertainty_modal_words_freq': 'Низкая степень уверенности',
            'call_to_action_dm_freq': 'Призыв к действию',
            'joint_action_freq': 'Совместное действие',
            'putting_emphasis_dm_freq': 'Акцентирование внимания',
            'refer_to_background_knowledge_freq': 'Отсылка к фоновым знаниям'
        }

        # Заполняем таблицу значениями для каждого показателя
        for feature_key in comparison_results[list(comparison_results.keys())[0]].keys():
            feature_name = feature_names.get(feature_key, feature_key)
            row = [feature_name]
            for db in comparison_results.keys():
                value = comparison_results[db].get(feature_key, "N/A")
                row.append(f"{value:.3f}" if isinstance(value, (int, float)) else value)
            table.add_row(*row)

        console.print(table)
        print(Fore.LIGHTWHITE_EX + "*" * 80)
        wait_for_enter_to_choose_opt()

    def print_miscellaneous_comparison_table(self, comparison_results):
        """Выводит сравнительные таблицы для показателей Miscellaneous features по корпусам"""

        pronoun_categories = [
            'avg_pers_possessive_pronouns_frequencies',
            'avg_reflexive_pronoun_frequencies',
            'avg_demonstrative_pronouns_frequencies',
            'avg_defining_pronouns_frequencies',
            'avg_relative_pronouns_frequencies',
            'avg_indefinite_pronouns_frequencies',
            'avg_negative_pronouns_frequencies'
        ]
        category_names = {
            'avg_pers_possessive_pronouns_frequencies': 'Личные и притяжательные местоимения',
            'avg_reflexive_pronoun_frequencies': 'Возвратные местоимения',
            'avg_demonstrative_pronouns_frequencies': 'Указательные местоимения',
            'avg_defining_pronouns_frequencies': 'Определительные местоимения',
            'avg_relative_pronouns_frequencies': 'Относительные местоимения',
            'avg_indefinite_pronouns_frequencies': 'Неопределенные местоимения',
            'avg_negative_pronouns_frequencies': 'Отрицательные местоимения'
        }

        for category in pronoun_categories:
            table = Table(title=category_names[category])
            table.add_column("Местоимение", justify="center", style="bold")
            for corpus_name in comparison_results.keys():
                table.add_column(corpus_name, justify="center")

            # Assuming that all corpora have the same set of pronouns for each category
            pronouns = set()
            for corpus_name, data in comparison_results.items():
                if category in data:
                    pronouns.update(data[category].keys())

            sorted_pronouns = sorted(pronouns,
                                     key=lambda x: comparison_results[list(comparison_results.keys())[0]].get(category,
                                                                                                              {}).get(x,
                                                                                                                      0),
                                     reverse=True)

            for pronoun in sorted_pronouns:
                row = [pronoun]
                for corpus_name in comparison_results.keys():
                    frequency = comparison_results[corpus_name].get(category, {}).get(pronoun, 0)
                    row.append(f"{frequency:.3f}%")
                table.add_row(*row)

            console.print(table)
            wait_for_enter_to_analyze()

        # Create a table for function words frequencies
        table_func_words = Table(title="Частоты служебных слов")
        table_func_words.add_column("Служебное слово", justify="center", style="bold")
        for corpus_name in comparison_results.keys():
            table_func_words.add_column(corpus_name, justify="center")

        func_words = set()
        for corpus_name, data in comparison_results.items():
            if 'avg_func_words_freq' in data:
                func_words.update(data['avg_func_words_freq'].keys())

        sorted_func_words = sorted(func_words, key=lambda x: comparison_results[list(comparison_results.keys())[0]].get(
            'avg_func_words_freq', {}).get(x, 0), reverse=True)

        for word in sorted_func_words:
            row = [word]
            for corpus_name in comparison_results.keys():
                frequency = comparison_results[corpus_name].get('avg_func_words_freq', {}).get(word, 0)
                row.append(f"{frequency:.3f}%")
            table_func_words.add_row(*row)

        console.print(table_func_words)
        wait_for_enter_to_analyze()

        # Create a table for punctuation frequencies
        table_punctuation = Table(title="Частоты знаков препинания всех токенов")
        table_punctuation.add_column("Знак препинания", justify="center", style="bold")
        for corpus_name in comparison_results.keys():
            table_punctuation.add_column(corpus_name, justify="center")

        punctuation_marks = set()
        for corpus_name, data in comparison_results.items():
            if 'avg_punct_normalized_frequency' in data:
                punctuation_marks.update(data['avg_punct_normalized_frequency'].keys())

        sorted_punctuation_marks = sorted(punctuation_marks,
                                          key=lambda x: comparison_results[list(comparison_results.keys())[0]].get(
                                              'avg_punct_normalized_frequency', {}).get(x, 0), reverse=True)

        for punct in sorted_punctuation_marks:
            row = [punct]
            for corpus_name in comparison_results.keys():
                frequency = comparison_results[corpus_name].get('avg_punct_normalized_frequency', {}).get(punct, 0)
                row.append(f"{frequency:.3f}%")
            table_punctuation.add_row(*row)

        console.print(table_punctuation)
        wait_for_enter_to_analyze()

        # Create a table for punctuation to all punctuation frequencies
        table_punct_to_all = Table(title="Частоты знаков препинания относительно всех знаков препинания")
        table_punct_to_all.add_column("Знак препинания", justify="center", style="bold")
        for corpus_name in comparison_results.keys():
            table_punct_to_all.add_column(corpus_name, justify="center")

        for punct in sorted_punctuation_marks:
            row = [punct]
            for corpus_name in comparison_results.keys():
                frequency = comparison_results[corpus_name].get('avg_punct_to_all_punct_frequency', {}).get(punct, 0)
                row.append(f"{frequency:.3f}%")
            table_punct_to_all.add_row(*row)

        console.print(table_punct_to_all)
        wait_for_enter_to_choose_opt()
