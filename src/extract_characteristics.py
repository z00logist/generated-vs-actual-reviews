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
    doc_sentence,
    syntax_parser,
) -> t.Sequence[str]:
    doc_sentence.parse_syntax(syntax_parser)
    return [token.rel for token in doc_sentence.tokens]


def process_review(
    text: str,
    morph_analyzer,
    segmenter,
    morph_tagger,
    syntax_parser,
) -> t.Sequence[t.Sequence[t.Mapping[str, str]]]:
    doc = natasha.Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)

    processed_sentences = []
    for sentence in doc.sents:
        processed_words = []
        for token in sentence.tokens:
            parsed_word = morph_analyzer.parse(token.text)[0]
            processed_words.append(
                {
                    "word": token.text,
                    "lemma": parsed_word.normal_form,
                    "pos": parsed_word.tag.POS,
                    "morph": str(parsed_word.tag),
                    "dep": token.rel,
                }
            )
        processed_sentences.append(processed_words)

    return processed_sentences


def convert_to_csv_format(
    processed_texts: t.Sequence[t.Sequence[t.Sequence[t.Mapping[str, str]]]]
) -> pd.DataFrame:
    rows = []
    for text in processed_texts:
        for sentence in text:
            sentence_text = " ".join(word["word"] for word in sentence)
            row = [sentence_text] + [
                word.get(attr, "")
                for word in sentence
                for attr in ["word", "lemma", "pos", "morph", "dep"]
            ]
            rows.append(row)

    max_length = max(len(sentence) for text in processed_texts for sentence in text)
    columns = ["sentence"] + [
        f"{attr}{i}"
        for i in range(1, max_length + 1)
        for attr in ["word", "lemma", "pos", "morph", "dep"]
    ]

    return pd.DataFrame(rows, columns=columns)


def main(data_path: str, column_name: str, output_path: str):
    df = pd.read_csv(data_path)
    components = initialize_analysis_components()
    process_function = lambda review: process_review(review, *components)
    preprocessed_data = df[column_name].apply(process_function).tolist()
    processed_df = convert_to_csv_format(preprocessed_data)
    processed_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process data file.")
    parser.add_argument("--data_path", type=str, help="Path to the data file.")
    parser.add_argument(
        "--column_name", type=str, help="Name of the column to process."
    )
    parser.add_argument("--output_path", type=str, help="Path for the output CSV file.")

    args = parser.parse_args()
    main(args.data_path, args.column_name, args.output_path)
