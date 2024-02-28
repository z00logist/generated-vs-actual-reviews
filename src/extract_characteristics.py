import typing as t

import argparse
import pandas as pd
import pymorphy2
import natasha


def initialize_analysis_components():
    morph_analyzer = pymorphy2.MorphAnalyzer()
    segmenter = natasha.Segmenter()
    embedding = natasha.NewsEmbedding()
    morph_tagger = natasha.NewsMorphTagger(embedding)
    syntax_parser = natasha.NewsSyntaxParser(embedding)

    return morph_analyzer, segmenter, morph_tagger, syntax_parser


def get_dependency_relations(
        text: str, 
        segmenter, 
        morph_tagger, 
        syntax_parser,
) -> t.Sequence[str]:
    doc = natasha.Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)
    return [token.rel for token in doc.tokens]


def process_review(
        text: str, 
        morph_analyzer, 
        segmenter, 
        morph_tagger, 
        syntax_parser,
) -> t.Sequence[t.Mapping[str, str]]:
    words = text.split()
    dep_relations = get_dependency_relations(
        text, 
        segmenter, 
        morph_tagger, 
        syntax_parser,
    )
    processed_words = []
    for word, dep in zip(words, dep_relations):
        parsed_word = morph_analyzer.parse(word)[0]
        processed_words.append(
            {
                "word": word,
                "lemma": parsed_word.normal_form,
                "pos": parsed_word.tag.POS,
                "morph": str(parsed_word.tag),
                "dep": dep,
            }
        )

    return processed_words


def convert_to_csv_format(
        processed_texts: t.Sequence[
            t.Sequence[
                t.Mapping[str, str]
            ]
        ]
) -> pd.DataFrame:
    max_length = max(len(review) for review in processed_texts)
    columns = ["sentence"] + [
        f"{attr}{i}"
        for i in range(1, max_length + 1)
        for attr in ["word", "lemma", "pos", "morph", "dep"]
    ]
    rows = []
    for text in processed_texts:
        sentence = " ".join(word["word"] for word in text)
        row = [sentence] + [
            word.get(attr, "")
            for i in range(max_length)
            for word in (text[i : i + 1] or [{}])
            for attr in ["word", "lemma", "pos", "morph", "dep"]
        ]
        rows.append(row)
    return pd.DataFrame(rows, columns=columns)


def main(data_path: str, column_name: str, outputh_path: str):
    df = pd.read_csv(data_path)

    morph_analyzer, segmenter, morph_tagger, syntax_parser = (
        initialize_analysis_components()
    )

    process_function = lambda review: process_review(
        review, 
        morph_analyzer, 
        segmenter, 
        morph_tagger,
        syntax_parser,
    )
    preprocessed_data = df[column_name].apply(process_function).tolist()

    processed_df = convert_to_csv_format(preprocessed_data)
    processed_df.to_csv(outputh_path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process data file.")
    parser.add_argument("--data_path", type=str, help="Path to the data file.")
    parser.add_argument("--column_name", type=str, help="Name of the column to process.")
    parser.add_argument("--output_path", type=str, help="Path for the output CSV file.")
    
    args = parser.parse_args()
    main(args.data_path, args.column_name, args.output_path)
