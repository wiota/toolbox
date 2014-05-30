from portphilio_lib.models import *


def build_db():
    # Drop everything
    Body.drop_collection()
    Medium.drop_collection()
    Subset.drop_collection()

    # Get the user object
    mc = User.objects.get(username="maggiecasey")

    range_urls = [
        "https://portphilio_maggiecasey.s3.amazonaws.com/Rangeweb01.jpg",
        "https://portphilio_maggiecasey.s3.amazonaws.com/BearingTheEcho01.jpg",
        "https:///portphilio_maggiecasey.s3.amazonaws.com/Range01.jpg"]

    range_media = [Photo(owner=mc, href=x, slug="", title="").save() for x in range_urls]

    range_work = Work(
        title="Range",
        slug="range",
        medium="Archival Ink Jet Print on Canvas",
        size="13' x 4'",
        date="2010",
        description="Range is a manipulated photograph taken of a military proving ground in Nevada. The resolution of the photograph was deliberately modified multiple times and layered together in a composite image. The resulting photograph appears to have multiple resolutions determined by the viewing distance.\nCollaboration between Maggie Casey and Jeffrey Stockbridge.",
        subset=range_media,
        owner=mc).save()
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
                                    owner=mc,
                                    subset=[]).save() for x in ins_dict_list]

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
            owner=mc).save() for x in scu_dict_list]

    scu_sub = Category(
        subset=scu_list,
        slug="sculpture",
        title="SCULPTURE",
        owner=mc).save()

    ins_sub = Category(
        subset=ins_list,
        slug="installations",
        title="INSTALLATIONS",
        owner=mc).save()

    Body(subset=[ins_sub, scu_sub], owner=mc).save()
