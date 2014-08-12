from toolbox.models import *

def clear_db(username):
    # Get the username
    u = User.objects.get(username=username)

    # Remove everything that the user owns
    for doc in [Medium, Vertex]:
        doc.objects(owner=u).delete()

    # Create an empty Body (since there is no endpoint for this)
    Body(owner=u, slug='', title='').save()

def build_db(username):
    clear_db(username)

    # Get the user object
    testuser = User.objects.get(username=username)

    range_urls = [
        "/image/TrainFromTurmoilToHappyClouds.jpg",
        "/image/Rangeweb01.jpg",
        "/image/BearingTheEcho01.jpg",
        "/image/Range01.jpg"]

    range_media = [Photo(owner=testuser, href=x, slug="", title="").save() for x in range_urls]

    range_work = Work(
        title="Range",
        slug="range",
        medium="Archival Ink Jet Print on Canvas",
        size="13' x 4'",
        date="2010",
        description="Range is a manipulated photograph taken of a military proving ground in Nevada. The resolution of the photograph was deliberately modified multiple times and layered together in a composite image. The resulting photograph appears to have multiple resolutions determined by the viewing distance.\nCollaboration between Maggie Casey and Jeffrey Stockbridge.",
        succset=range_media,
        owner=testuser).save()
    ins_dict_list = [
        {"title": "Gold Tooth", "slug": "gold-tooth"},
        {"title": "Processions: an Elaborative Cartography", "slug": "processions-an-elaborative-cartography"},
        {"title": "Gold Tooth; Tapestries", "slug": "gold-tooth-tapestries"},
        {"title": "Feathers", "slug": "feathers"},
        {"title": "Staircase", "slug": "staircase"},
        {"title": "Two Chairs", "slug": "two-chairs"},
        {"title": "Duck and Silkworm Celebrate Synthetic Advancement", "slug": "duck-and-silkworm-celebrate-synthetic-advancement"}]

    ins_list = [range_work] + [Work(title=x['title'],
                                    slug=x['slug'],
                                    owner=testuser,).save() for x in ins_dict_list]

    scu_dict_list = [
        {"title": "Breaker", "slug": "breaker"},
        {"title": "Cover", "slug": "cover"},
        {"title": "Heap", "slug": "heap"},
        {"title": "Comma", "slug": "comma"},
        {"title": "Memorial to Tray Anning", "slug": "memorial-to-tray-anning"},
        {"title": "Hers", "slug": "hers"},
        {"title": "Model: Cloud", "slug": "model-cloud"},
        {"title": "Model: Splitting", "slug": "model-splitting"},
        {"title": "Model: Hanging Angle", "slug": "model-hanging-angle"}]

    scu_list = [
        Work(
            title=x['title'],
            slug=x['slug'],
            owner=testuser).save() for x in scu_dict_list]

    scu_sub = Category(
        succset=scu_list,
        slug="sculpture",
        title="SCULPTURE",
        owner=testuser).save()

    ins_sub = Category(
        succset=ins_list,
        slug="installations",
        title="INSTALLATIONS",
        owner=testuser).save()

    body = Body.objects.get(owner=testuser)
    body.succset = [ins_sub, scu_sub]
    body.save()

    ## And now for some really crazy shit...

    # Add a work to the body
    bw = Work(title="Bodywork", slug="bodywork", owner=testuser).save()
    body.succset = body.succset + [bw]
    body.save()

    # Add a category to a category
    newcat = Category(title="Cats and Kittens", owner=testuser).save()
    ins = Category.objects.get(slug="installations", owner=testuser)
    ins.succset = ins.succset + [newcat]
    ins.save()

    # Slugtest
    slugcat = Category(title="CATS!!! AND!!! KITTENS!!!", owner=testuser).save()
    body.succset = body.succset + [slugcat]
    body.save()

    # Add a work to a category
    ins.succset = ins.succset + [bw]
    ins.save()

    # Add an existing category to the body
    newcat = Category.objects.get(slug="cats-and-kittens", owner=testuser)
    body.succset = body.succset + [newcat]
    body.save()

    # Add a Work and a Category to a Work
    rang = Work.objects.get(owner=testuser, slug="range")
    newcat = Category.objects.get(slug="cats-and-kittens", owner=testuser)
    rang.succset = rang.succset + [bw, newcat]
    rang.save()
