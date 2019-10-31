import csv
import json
import operator
import os.path
from collections import OrderedDict, defaultdict


def construct_comment(body):
    comment = []
    for b in body:
        if b["type"] == 'Paragraph':
            comment.append(b["value"]["value"])
        elif b["type"] == 'Paragraph':
            pass

    return


def convert_json_to_csv(filename):
    with open(filename) as f:
        data = json.load(f)

    post_id, _ = os.path.splitext(filename)

    # {comment_id: [comment1, comment2, ...]}
    comments = defaultdict(list)

    for c in data:
        comments[c['reply']['parentId']].append(c)

    csv_filename = f'comments_{post_id}.csv'
    with open(csv_filename, "w") as csv_file:
        author_itemgetter = operator.itemgetter("author")
        mapping = OrderedDict([
            ('comment id', operator.itemgetter("id")),
            ('display name', lambda x: operator.itemgetter('displayName')(author_itemgetter(x))),
            ('screen name',  lambda x: operator.itemgetter('screenName')(author_itemgetter(x))),
            ('comment',  operator.itemgetter("plaintext")),
            ('likes',  operator.itemgetter("likes")),
        ])
        writer = csv.DictWriter(csv_file, fieldnames=mapping.keys())

        writer.writeheader()

        for comment_id, comments in comments.items():
            for c in sorted(comments, key=lambda x: x['publishTime']['timestamp']):
                r = c['reply']
                writer.writerow({
                    k: v(r)
                    for k, v in mapping.items()
                })

    print(f'Wrote {csv_filename}')


if __name__ == '__main__':
    import sys

    convert_json_to_csv(sys.argv[1])
