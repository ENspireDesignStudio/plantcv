#!/usr/bin/env python

import pytest
import os
import shutil
import numpy as np
import cv2
import plantcv as pcv
# Import matplotlib and use a null Template to block plotting to screen
# This will let us test debug = "plot"
import matplotlib
matplotlib.use('Template')

TEST_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TEST_TMPDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cache")
TEST_COLOR_DIM = (2056, 2454, 3)
TEST_GRAY_DIM = (2056, 2454)
TEST_BINARY_DIM = TEST_GRAY_DIM
TEST_INPUT_COLOR = "input_color_img.jpg"
TEST_INPUT_GRAY = "input_gray_img.jpg"
TEST_INPUT_BINARY = "input_binary_img.png"
TEST_INPUT_ROI = "input_roi.npz"
TEST_INPUT_CONTOURS = "input_contours.npz"
TEST_VIS = "VIS_SV_0_z300_h1_g0_e85_v500_93054.png"
TEST_NIR = "NIR_SV_0_z300_h1_g0_e15000_v500_93059.png"
TEST_INPUT_MASK = "input_mask.png"
TEST_INPUT_NIR_MASK = "input_nir.png"
TEST_INPUT_FDARK = "FLUO_TV_dark.png"
TEST_INPUT_FMIN = "FLUO_TV_min.png"
TEST_INPUT_FMAX = "FLUO_TV_max.png"
TEST_INPUT_FMASK = "FLUO_TV_MASK.png"
TEST_INTPUT_GREENMAG = "input_green-magenta.jpg"
TEST_INTPUT_MULTI = "multi_ori_image.jpg"
TEST_INPUT_MULTI_CONTOUR = "roi_objects.npz"
TEST_INPUT_ClUSTER_CONTOUR = "clusters_i.npz"
TEST_INPUT_CROPPED = 'cropped_img.jpg'
TEST_INPUT_CROPPED_MASK = 'cropped-mask.png'
TEST_INPUT_MARKER = 'seed-image.jpg'
TEST_FOREGROUND = "TEST_FOREGROUND.jpg"
TEST_BACKGROUND = "TEST_BACKGROUND.jpg"
TEST_PDFS = "naive_bayes_pdfs.txt"


if not os.path.exists(TEST_TMPDIR):
    os.mkdir(TEST_TMPDIR)


def test_plantcv_adaptive_threshold():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_GRAY), -1)
    # Test with debug = "print"
    _, _ = pcv.adaptive_threshold(img=img, maxValue=255, thres_type="gaussian", object_type="light", device=0,
                                  debug="print")
    os.rename("1_adaptive_threshold_gaussian.png", os.path.join(TEST_TMPDIR, "1_adaptive_threshold_gaussian.png"))
    # Test with debug = "plot"
    _, _ = pcv.adaptive_threshold(img=img, maxValue=255, thres_type="gaussian", object_type="light", device=0,
                                  debug="plot")
    # Test with debug = None
    device, binary_img = pcv.adaptive_threshold(img=img, maxValue=255, thres_type="gaussian", object_type="light",
                                                device=0, debug=None)
    # Assert that the output image has the dimensions of the input image
    if all([i == j] for i, j in zip(np.shape(binary_img), TEST_GRAY_DIM)):
        # Assert that the image is binary
        if all([i == j] for i, j in zip(np.unique(binary_img), [0, 255])):
            assert 1
        else:
            assert 0
    else:
        assert 0


def test_plantcv_analyze_bound():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    mask = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    contours_npz = np.load(os.path.join(TEST_DATA, TEST_INPUT_CONTOURS))
    object_contours = contours_npz['arr_0']
    # Test with debug = "print"
    outfile = os.path.join(TEST_TMPDIR, TEST_INPUT_COLOR)
    _, _, _, _ = pcv.analyze_bound(img=img, imgname="img", obj=object_contours[0], mask=mask, line_position=300,
                                   device=0, debug="print", filename=outfile)
    os.rename("1_boundary_on_img.jpg", os.path.join(TEST_TMPDIR, "1_boundary_on_img.jpg"))
    os.rename("1_boundary_on_white.jpg", os.path.join(TEST_TMPDIR, "1_boundary_on_white.jpg"))
    # Test with debug = "plot"
    _, _, _, _ = pcv.analyze_bound(img=img, imgname="img", obj=object_contours[0], mask=mask, line_position=300,
                                   device=0, debug="plot", filename=False)
    # Test with debug = None
    device, boundary_header, boundary_data, boundary_img1 = pcv.analyze_bound(img=img, imgname="img",
                                                                              obj=object_contours[0], mask=mask,
                                                                              line_position=300, device=0,
                                                                              debug=None, filename=False)
    assert boundary_data[3] == 596347


def test_plantcv_analyze_color():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    mask = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    # Test with debug = "print"
    outfile = os.path.join(TEST_TMPDIR, TEST_INPUT_COLOR)
    _, _, _, _ = pcv.analyze_color(img=img, imgname="img", mask=mask, bins=256, device=0, debug="print",
                                   hist_plot_type=None, pseudo_channel="v", pseudo_bkg="img", resolution=300,
                                   filename=outfile)
    os.rename("1_pseudocolor.jpg", os.path.join(TEST_TMPDIR, "1_pseudocolor.jpg"))
    # Test with debug = "plot"
    _, _, _, _ = pcv.analyze_color(img=img, imgname="img", mask=mask, bins=256, device=0, debug="plot",
                                   hist_plot_type=None, pseudo_channel="v", pseudo_bkg="img", resolution=300,
                                   filename=False)
    # Test with debug = None
    device, color_header, color_data, analysis_images = pcv.analyze_color(img=img, imgname="img", mask=mask, bins=256,
                                                                          device=0, debug=None, hist_plot_type=None,
                                                                          pseudo_channel="v", pseudo_bkg="img",
                                                                          resolution=300, filename=False)
    assert np.sum(color_data[3]) != 0


def test_plantcv_analyze_nir():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR), 0)
    mask = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    # Test with debug = "print"
    outfile = os.path.join(TEST_TMPDIR, TEST_INPUT_COLOR)
    _, _, _, _ = pcv.analyze_NIR_intensity(img=img, rgbimg=img, mask=mask, bins=256, device=0, histplot=False,
                                           debug="print", filename=outfile)
    os.rename("3_nir_pseudo_plant.jpg", os.path.join(TEST_TMPDIR, "3_nir_pseudo_plant.jpg"))
    os.rename("3_nir_pseudo_plant_back.jpg", os.path.join(TEST_TMPDIR, "3_nir_pseudo_plant_back.jpg"))
    # Test with debug = "plot"
    _, _, _, _ = pcv.analyze_NIR_intensity(img=img, rgbimg=img, mask=mask, bins=256, device=0, histplot=False,
                                           debug="plot", filename=False)
    # Test with debug = None
    device, hist_header, hist_data, h_norm = pcv.analyze_NIR_intensity(img=img, rgbimg=img, mask=mask, bins=256,
                                                                       device=0, histplot=False, debug=None,
                                                                       filename=False)
    assert np.sum(hist_data[3]) == 713986


def test_plantcv_analyze_object():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    mask = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    contours_npz = np.load(os.path.join(TEST_DATA, TEST_INPUT_CONTOURS))
    obj_contour = contours_npz['arr_0']
    max_obj = max(obj_contour, key=len)
    # Test with debug = "print"
    outfile = os.path.join(TEST_TMPDIR, TEST_INPUT_COLOR)
    _, _, _, _ = pcv.analyze_object(img=img, imgname="img", obj=max_obj, mask=mask, device=0, debug="print",
                                    filename=outfile)
    os.rename("1_shapes.jpg", os.path.join(TEST_TMPDIR, "1_shapes.jpg"))
    # Test with debug = "plot"
    _, _, _, _ = pcv.analyze_object(img=img, imgname="img", obj=max_obj, mask=mask, device=0, debug="plot",
                                    filename=False)
    # Test with debug = None
    device, obj_header, obj_data, obj_images = pcv.analyze_object(img=img, imgname="img", obj=max_obj, mask=mask,
                                                                  device=0, debug=None, filename=False)
    assert obj_data[1] != 0


def test_plantcv_apply_mask():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    mask = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    # Test with debug = "print"
    _, _ = pcv.apply_mask(img=img, mask=mask, mask_color="white", device=0, debug="print")
    os.rename("1_wmasked.png", os.path.join(TEST_TMPDIR, "1_wmasked.png"))
    # Test with debug = "plot"
    _, _ = pcv.apply_mask(img=img, mask=mask, mask_color="white", device=0, debug="plot")
    # Test with debug = None
    device, masked_img = pcv.apply_mask(img=img, mask=mask, mask_color="white", device=0, debug=None)
    assert all([i == j] for i, j in zip(np.shape(masked_img), TEST_COLOR_DIM))


def test_plantcv_auto_crop():
    img1 = cv2.imread(os.path.join(TEST_DATA, TEST_INTPUT_MULTI), -1)
    contours = np.load(os.path.join(TEST_DATA, TEST_INPUT_MULTI_CONTOUR))
    roi_contours = contours['arr_0']
    # Test with debug = "print"
    _, _ = pcv.auto_crop(device=0, img=img1, objects=roi_contours[48], padding_x=20, padding_y=20, color='black',
                         debug="print")
    os.rename("1_crop_area.png", os.path.join(TEST_TMPDIR, "1_crop_area.png"))
    os.rename("1_auto_cropped.png", os.path.join(TEST_TMPDIR, "1_auto_cropped.png"))
    # Test with debug = "plot"
    _, _ = pcv.auto_crop(device=0, img=img1, objects=roi_contours[48], padding_x=20, padding_y=20, color='black',
                         debug="plot")
    # Test with debug = None
    device, cropped = pcv.auto_crop(device=0, img=img1, objects=roi_contours[48], padding_x=20, padding_y=20,
                                    color='black', debug=None)
    x, y, z = np.shape(img1)
    x1, y1, z1 = np.shape(cropped)
    assert x > x1


def test_plantcv_binary_threshold():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_GRAY), -1)
    # Test with debug = "print"
    _, _ = pcv.binary_threshold(img=img, threshold=25, maxValue=255, object_type="light", device=0, debug="print")
    os.rename("1_binary_threshold25.png", os.path.join(TEST_TMPDIR, "1_binary_threshold25.png"))
    # Test with debug = "plot"
    _, _ = pcv.binary_threshold(img=img, threshold=25, maxValue=255, object_type="light", device=0, debug="plot")
    # Test with debug = None
    device, binary_img = pcv.binary_threshold(img=img, threshold=25, maxValue=255, object_type="light",
                                              device=0, debug=None)
    # Assert that the output image has the dimensions of the input image
    if all([i == j] for i, j in zip(np.shape(binary_img), TEST_GRAY_DIM)):
        # Assert that the image is binary
        if all([i == j] for i, j in zip(np.unique(binary_img), [0, 255])):
            assert 1
        else:
            assert 0
    else:
        assert 0


def test_plantcv_cluster_contours():
    img1 = cv2.imread(os.path.join(TEST_DATA, TEST_INTPUT_MULTI), -1)
    contours = np.load(os.path.join(TEST_DATA, TEST_INPUT_MULTI_CONTOUR))
    roi_contours = contours['arr_0']
    # Test with debug = "print"
    _, _, _ = pcv.cluster_contours(device=0, img=img1, roi_objects=roi_contours, nrow=4, ncol=6, debug="print")
    os.rename("1_clusters.png", os.path.join(TEST_TMPDIR, "1_clusters.png"))
    # Test with debug = "plot"
    _, _, _ = pcv.cluster_contours(device=0, img=img1, roi_objects=roi_contours, nrow=4, ncol=6, debug="plot")
    # Test with debug = None
    device, clusters_i, contours = pcv.cluster_contours(device=0, img=img1, roi_objects=roi_contours, nrow=4,
                                                        ncol=6, debug=None)
    lenori = len(roi_contours)
    lenclust = len(clusters_i)
    assert lenori > lenclust


def test_plantcv_cluster_contours_splitimg():
    img1 = cv2.imread(os.path.join(TEST_DATA, TEST_INTPUT_MULTI), -1)
    contours = np.load(os.path.join(TEST_DATA, TEST_INPUT_MULTI_CONTOUR))
    clusters = np.load(os.path.join(TEST_DATA, TEST_INPUT_ClUSTER_CONTOUR))
    roi_contours = contours['arr_0']
    cluster_contours = clusters['arr_0']
    # Test with debug = "print"
    _, _ = pcv.cluster_contour_splitimg(device=0, img=img1, grouped_contour_indexes=cluster_contours,
                                        contours=roi_contours, outdir=TEST_TMPDIR, file=None, filenames=None,
                                        debug="print")
    for i in range(1, 19):
        os.rename(str(i) + "_clusters.png", os.path.join(TEST_TMPDIR, str(i) + "_clusters.png"))
        os.rename(str(i) + "_wmasked.png", os.path.join(TEST_TMPDIR, str(i) + "_wmasked.png"))
    # Test with debug = "plot"
    _, _ = pcv.cluster_contour_splitimg(device=0, img=img1, grouped_contour_indexes=cluster_contours,
                                        contours=roi_contours, outdir=None, file=None, filenames=None, debug="plot")
    # Test with debug = None
    device, output_path = pcv.cluster_contour_splitimg(device=0, img=img1, grouped_contour_indexes=cluster_contours,
                                                       contours=roi_contours, outdir=None, file=None,
                                                       filenames=None, debug=None)
    assert len(output_path) != 0


def test_plantcv_crop_position_mask():
    nir, path1, filename1 = pcv.readimage(os.path.join(TEST_DATA, TEST_INPUT_NIR_MASK))
    mask = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_MASK), -1)
    # Test with debug = "print"
    _, _ = pcv.crop_position_mask(nir, mask, device=0, x=40, y=3, v_pos="top", h_pos="right", debug="print")
    os.rename("1_mask_overlay.png", os.path.join(TEST_TMPDIR, "1_mask_overlay.png"))
    os.rename("1_newmask.png", os.path.join(TEST_TMPDIR, "1_newmask.png"))
    os.rename("1_push-right.png", os.path.join(TEST_TMPDIR, "1_push-right.png"))
    os.rename("1_push-top_.png", os.path.join(TEST_TMPDIR, "1_push-top_.png"))
    # Test with debug = "plot"
    _, _ = pcv.crop_position_mask(nir, mask, device=0, x=40, y=3, v_pos="top", h_pos="right", debug="plot")
    # Test with debug = None
    device, newmask = pcv.crop_position_mask(nir, mask, device=0, x=40, y=3, v_pos="top", h_pos="right", debug=None)
    assert np.sum(newmask) == 641517


def test_plantcv_define_roi():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    # Test with debug = "print"
    _, _, _ = pcv.define_roi(img=img, shape="rectangle", device=0, roi=None, roi_input="default", debug="print",
                             adjust=True, x_adj=600, y_adj=300, w_adj=-300, h_adj=-600)
    os.rename("1_roi.png", os.path.join(TEST_TMPDIR, "1_roi.png"))
    # Test with debug = "plot"
    _, _, _ = pcv.define_roi(img=img, shape="rectangle", device=0, roi=None, roi_input="default", debug="plot",
                             adjust=True, x_adj=600, y_adj=300, w_adj=-300, h_adj=-600)
    # Test with debug = None
    device, contours, hierarchy = pcv.define_roi(img=img, shape="rectangle", device=0, roi=None, roi_input="default",
                                                 debug=None, adjust=True, x_adj=600, y_adj=300, w_adj=-300, h_adj=-600)
    # Assert the contours and hierarchy lists contain only the ROI
    if len(contours) == 2 and len(hierarchy) == 1:
        assert 1
    else:
        assert 0


def test_plantcv_dilate():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    # Test with debug = "print"
    _, _ = pcv.dilate(img=img, kernel=5, i=1, device=0, debug="print")
    os.rename("1_dil_image_itr_1.png", os.path.join(TEST_TMPDIR, "1_dil_image_itr_1.png"))
    # Test with debug = "plot"
    _, _ = pcv.dilate(img=img, kernel=5, i=1, device=0, debug="plot")
    # Test with debug = None
    device, dilate_img = pcv.dilate(img=img, kernel=5, i=1, device=0, debug=None)
    # Assert that the output image has the dimensions of the input image
    if all([i == j] for i, j in zip(np.shape(dilate_img), TEST_BINARY_DIM)):
        # Assert that the image is binary
        if all([i == j] for i, j in zip(np.unique(dilate_img), [0, 255])):
            assert 1
        else:
            assert 0
    else:
        assert 0


def test_plantcv_erode():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    # Test with debug = "print"
    _, _ = pcv.erode(img=img, kernel=5, i=1, device=0, debug="print")
    os.rename("1_er_image_itr_1.png", os.path.join(TEST_TMPDIR, "1_er_image_itr_1.png"))
    # Test with debug = "plot"
    _, _ = pcv.erode(img=img, kernel=5, i=1, device=0, debug="plot")
    # Test with debug = None
    device, erode_img = pcv.erode(img=img, kernel=5, i=1, device=0, debug=None)
    # Assert that the output image has the dimensions of the input image
    if all([i == j] for i, j in zip(np.shape(erode_img), TEST_BINARY_DIM)):
        # Assert that the image is binary
        if all([i == j] for i, j in zip(np.unique(erode_img), [0, 255])):
            assert 1
        else:
            assert 0
    else:
        assert 0


def test_plantcv_fatal_error():
    # Verify that the fatal_error function raises a RuntimeError
    with pytest.raises(RuntimeError):
        pcv.fatal_error("Test error")


def test_plantcv_fill():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    # Test with debug = "print"
    mask = np.copy(img)
    _, _ = pcv.fill(img=img, mask=mask, size=1, device=0, debug="print")
    os.rename("1_fill1.png", os.path.join(TEST_TMPDIR, "1_fill1.png"))
    # Test with debug = "plot"
    mask = np.copy(img)
    _, _ = pcv.fill(img=img, mask=mask, size=1, device=0, debug="plot")
    # Test with debug = None
    mask = np.copy(img)
    device, fill_img = pcv.fill(img=img, mask=mask, size=1, device=0, debug=None)
    # Assert that the output image has the dimensions of the input image
    assert all([i == j] for i, j in zip(np.shape(fill_img), TEST_BINARY_DIM))


def test_plantcv_find_objects():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    mask = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    # Test with debug = "print"
    _, _, _ = pcv.find_objects(img=img, mask=mask, device=0, debug="print")
    os.rename("1_id_objects.png", os.path.join(TEST_TMPDIR, "1_id_objects.png"))
    # Test with debug = "plot"
    _, _, _ = pcv.find_objects(img=img, mask=mask, device=0, debug="plot")
    # Test with debug = None
    device, contours, hierarchy = pcv.find_objects(img=img, mask=mask, device=0, debug=None)
    # Assert the correct number of contours are found
    assert len(contours) == 7341


def test_plantcv_flip():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    # Test with debug = "print"
    _, _ = pcv.flip(img=img, direction="horizontal", device=0, debug="print")
    os.rename("1_flipped.png", os.path.join(TEST_TMPDIR, "1_flipped.png"))
    # Test with debug = "plot"
    _, _ = pcv.flip(img=img, direction="horizontal", device=0, debug="plot")
    # Test with debug = None
    device, flipped_img = pcv.flip(img=img, direction="horizontal", device=0, debug=None)
    assert all([i == j] for i, j in zip(np.shape(flipped_img), TEST_COLOR_DIM))


def test_plantcv_fluor_fvfm():
    fdark = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_FDARK), -1)
    fmin = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_FMIN), -1)
    fmax = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_FMAX), -1)
    fmask = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_FMASK), -1)
    # Test with debug = "print"
    outfile = os.path.join(TEST_TMPDIR, TEST_INPUT_FMAX)
    _, _, _ = pcv.fluor_fvfm(fdark=fdark, fmin=fmin, fmax=fmax, mask=fmask, device=0, filename=outfile, bins=1000,
                             debug="print")
    os.rename("1_fmin_mask.png", os.path.join(TEST_TMPDIR, "1_fmin_mask.png"))
    os.rename("1_fmax_mask.png", os.path.join(TEST_TMPDIR, "1_fmax_mask.png"))
    os.rename("1_fv_convert.png", os.path.join(TEST_TMPDIR, "1_fv_convert.png"))
    # Test with debug = "plot"
    _, _, _ = pcv.fluor_fvfm(fdark=fdark, fmin=fmin, fmax=fmax, mask=fmask, device=0, filename=False, bins=1000,
                             debug="plot")
    # Test with debug = None
    device, fvfm_header, fvfm_data = pcv.fluor_fvfm(fdark=fdark, fmin=fmin, fmax=fmax, mask=fmask, device=0,
                                                    filename=False, bins=1000, debug=None)
    assert fvfm_data[4] > 0.66


def test_plantcv_gaussian_blur():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    # Test with debug = "print"
    _, _ = pcv.gaussian_blur(device=0, img=img, ksize=(51, 51), sigmax=0, sigmay=None, debug="print")
    os.rename("1_gaussian_blur.png", os.path.join(TEST_TMPDIR, "1_gaussian_blur.png"))
    # Test with debug = "plot"
    _, _ = pcv.gaussian_blur(device=0, img=img, ksize=(51, 51), sigmax=0, sigmay=None, debug="plot")
    # Test with debug = None
    device, gaussian_img = pcv.gaussian_blur(device=0, img=img, ksize=(51, 51), sigmax=0, sigmay=None, debug=None)
    imgavg = np.average(img)
    gavg = np.average(gaussian_img)
    assert gavg != imgavg


def test_plantcv_get_nir():
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, nirpath = pcv.get_nir(TEST_DATA, TEST_VIS, device=0, debug=None)
    nirpath1 = os.path.join(TEST_DATA, TEST_NIR)
    assert nirpath == nirpath1


def test_plantcv_hist_equalization():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_GRAY), -1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, hist = pcv.hist_equalization(img, device=0, debug=None)
    histavg = np.average(hist)
    imgavg = np.average(img)
    assert histavg != imgavg


def test_plantcv_image_add():
    img1 = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    img2 = np.copy(img1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, added_img = pcv.image_add(img1=img1, img2=img2, device=0, debug=None)
    assert all([i == j] for i, j in zip(np.shape(added_img), TEST_BINARY_DIM))


def test_plantcv_image_subtract():
    img1 = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    img2 = np.copy(img1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, subtract_img = pcv.image_subtract(img1=img1, img2=img2, device=0, debug=None)
    assert all([i == j] for i, j in zip(np.shape(subtract_img), TEST_BINARY_DIM))


def test_plantcv_invert():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, inverted_img = pcv.invert(img=img, device=0, debug=None)
    # Assert that the output image has the dimensions of the input image
    if all([i == j] for i, j in zip(np.shape(inverted_img), TEST_BINARY_DIM)):
        # Assert that the image is binary
        if all([i == j] for i, j in zip(np.unique(inverted_img), [0, 255])):
            assert 1
        else:
            assert 0
    else:
        assert 0


def test_plantcv_laplace_filter():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_GRAY), -1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, lp_img = pcv.laplace_filter(img=img, k=1, scale=1, device=0, debug=None)
    # Assert that the output image has the dimensions of the input image
    assert all([i == j] for i, j in zip(np.shape(lp_img), TEST_GRAY_DIM))


def test_plantcv_logical_and():
    img1 = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    img2 = np.copy(img1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, and_img = pcv.logical_and(img1=img1, img2=img2, device=0, debug=None)
    assert all([i == j] for i, j in zip(np.shape(and_img), TEST_BINARY_DIM))


def test_plantcv_logical_or():
    img1 = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    img2 = np.copy(img1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, or_img = pcv.logical_or(img1=img1, img2=img2, device=0, debug=None)
    assert all([i == j] for i, j in zip(np.shape(or_img), TEST_BINARY_DIM))


def test_plantcv_logical_xor():
    img1 = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    img2 = np.copy(img1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, xor_img = pcv.logical_xor(img1=img1, img2=img2, device=0, debug=None)
    assert all([i == j] for i, j in zip(np.shape(xor_img), TEST_BINARY_DIM))


def test_plantcv_median_blur():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, blur_img = pcv.median_blur(img=img, ksize=5, device=0, debug=None)
    # Assert that the output image has the dimensions of the input image
    if all([i == j] for i, j in zip(np.shape(blur_img), TEST_BINARY_DIM)):
        # Assert that the image is binary
        if all([i == j] for i, j in zip(np.unique(blur_img), [0, 255])):
            assert 1
        else:
            assert 0
    else:
        assert 0


def test_plantcv_naive_bayes_classifier():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, mask = pcv.naive_bayes_classifier(img=img, pdf_file=os.path.join(TEST_DATA, TEST_PDFS),
                                              device=0, debug=None)

    # Assert that the output image has the dimensions of the input image
    if all([i == j] for i, j in zip(np.shape(mask), TEST_GRAY_DIM)):
        # Assert that the image is binary
        if all([i == j] for i, j in zip(np.unique(mask), [0, 255])):
            assert 1
        else:
            assert 0
    else:
        assert 0


def test_plantcv_object_composition():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    contours_npz = np.load(os.path.join(TEST_DATA, TEST_INPUT_CONTOURS))
    object_contours = contours_npz['arr_0']
    object_hierarchy = contours_npz['arr_1']
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, contours, mask = pcv.object_composition(img=img, contours=object_contours, hierarchy=object_hierarchy,
                                                    device=0, debug=None)
    # Assert that the objects have been combined
    contour_shape = np.shape(contours)
    assert contour_shape[1] == 1


def test_plantcv_otsu_threshold():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INTPUT_GREENMAG), -1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, threshold_otsu = pcv.otsu_auto_threshold(img, 255, 'dark', device=0, debug=None)
    assert np.max(threshold_otsu) == 255


def test_plantcv_output_mask():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_GRAY), -1)
    mask = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_BINARY), -1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, imgpath, maskpath, analysis_images = pcv.output_mask(0, img, mask, 'test.png', TEST_DATA,
                                                                 mask_only=False, debug=None)
    path = str(TEST_DATA) + '/ori-images'
    path1 = str(TEST_DATA) + '/mask-images'
    assert all([os.path.exists(path) is True, os.path.exists(path1) is True])
    shutil.rmtree(path)
    shutil.rmtree(path1)


def test_plantcv_plot_hist():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR), -1)
    bins, hist = pcv.plot_hist(img, False)
    assert len(hist) == 256


def test_plantcv_print_image():
    img, path, img_name = pcv.readimage(filename=os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    filename = os.path.join(TEST_TMPDIR, 'plantcv_print_image.jpg')
    pcv.print_image(img=img, filename=filename)
    # Assert that the file was created
    assert os.path.exists(filename) is True


def test_plantcv_print_results():
    header = ['field1', 'field2', 'field3']
    data = ['value1', 'value2', 'value3']
    pcv.print_results(filename='not_used', header=header, data=data)


def test_plantcv_readimage():
    img, path, img_name = pcv.readimage(filename=os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    # Assert that the image name returned equals the name of the input image
    # Assert that the path of the image returned equals the path of the input image
    # Assert that the dimensions of the returned image equals the expected dimensions
    if img_name == TEST_INPUT_COLOR and path == TEST_DATA:
        if all([i == j] for i, j in zip(np.shape(img), TEST_COLOR_DIM)):
            assert 1
        else:
            assert 0
    else:
        assert 0


def test_plantcv_rectangle_mask():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_GRAY), -1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, masked, hist, contour, heir = pcv.rectangle_mask(img, (0, 0), (2454, 2056), device=0,
                                                             debug=None, color="black")
    maskedsum = np.sum(masked)
    imgsum = np.sum(img)
    assert maskedsum < imgsum


def test_plantcv_report_size_marker():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_MARKER), -1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, marker_header, marker_data, images = pcv.report_size_marker_area(img, 'rectangle', 0, debug=None,
                                                                             marker='detect', x_adj=3500, y_adj=600,
                                                                             w_adj=-100, h_adj=-1500, base='white',
                                                                             objcolor='light', thresh_channel='s',
                                                                             thresh=120, filename=False)
    assert marker_data[1] > 100


def test_plantcv_resize():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, resized_img = pcv.resize(img, 0.5, 0.5, device=0, debug=None)
    ix, iy, iz = np.shape(img)
    rx, ry, rz = np.shape(resized_img)
    assert ix > rx


def test_plantcv_rgb2gray_hsv():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, s = pcv.rgb2gray_hsv(img=img, channel='s', device=0, debug=None)
    # Assert that the output image has the dimensions of the input image but is only a single channel
    assert all([i == j] for i, j in zip(np.shape(s), TEST_GRAY_DIM))


def test_plantcv_rgb2gray_lab():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, b = pcv.rgb2gray_lab(img=img, channel='b', device=0, debug=None)
    # Assert that the output image has the dimensions of the input image but is only a single channel
    assert all([i == j] for i, j in zip(np.shape(b), TEST_GRAY_DIM))


def test_plantcv_rgb2gray():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, gray = pcv.rgb2gray(img=img, device=0, debug=None)
    # Assert that the output image has the dimensions of the input image but is only a single channel
    assert all([i == j] for i, j in zip(np.shape(gray), TEST_GRAY_DIM))


def test_plantcv_roi_objects():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    roi_npz = np.load(os.path.join(TEST_DATA, TEST_INPUT_ROI))
    roi_contour = roi_npz['arr_0']
    roi_hierarchy = roi_npz['arr_1']
    contours_npz = np.load(os.path.join(TEST_DATA, TEST_INPUT_CONTOURS))
    object_contours = contours_npz['arr_0']
    object_hierarchy = contours_npz['arr_1']
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, kept_contours, kept_hierarchy, mask, area = pcv.roi_objects(img=img, roi_type="partial",
                                                                        roi_contour=roi_contour,
                                                                        roi_hierarchy=roi_hierarchy,
                                                                        object_contour=object_contours,
                                                                        obj_hierarchy=object_hierarchy,
                                                                        device=0, debug=None)
    # Assert that the contours were filtered as expected
    assert len(kept_contours) == 1046


def test_plantcv_rotate_img():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, rotated = pcv.rotate_img(img, 45, device=0, debug=None)
    imgavg = np.average(img)
    rotateavg = np.average(rotated)
    assert rotateavg != imgavg


def test_plantcv_scharr_filter():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_GRAY), -1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, scharr_img = pcv.scharr_filter(img=img, dX=1, dY=0, scale=1, device=0, debug=None)
    # Assert that the output image has the dimensions of the input image
    assert all([i == j] for i, j in zip(np.shape(scharr_img), TEST_GRAY_DIM))


def test_plantcv_shift_img():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_COLOR))
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, rotated = pcv.shift_img(img, device=0, number=300, side="top", debug=None)
    imgavg = np.average(img)
    shiftavg = np.average(rotated)
    assert shiftavg != imgavg


def test_plantcv_sobel_filter():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_GRAY), -1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, sobel_img = pcv.sobel_filter(img=img, dx=1, dy=0, k=1, device=0, debug=None)
    # Assert that the output image has the dimensions of the input image
    assert all([i == j] for i, j in zip(np.shape(sobel_img), TEST_GRAY_DIM))


def test_plantcv_triangle_threshold():
    img1 = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_GRAY), -1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, thresholded = pcv.triangle_auto_threshold(0, img1, 255, "light", 10, debug=None)
    thresholdedavg = np.average(thresholded)
    imgavg = np.average(img1)
    assert thresholdedavg > imgavg


def test_plantcv_watershed_segmentation():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_CROPPED))
    mask = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_CROPPED_MASK), -1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, watershed_header, watershed_data, images = pcv.watershed_segmentation(0, img, mask, distance=10,
                                                                                  filename=False, debug=None)
    assert watershed_data[1] > 9


def test_plantcv_white_balance():
    img = cv2.imread(os.path.join(TEST_DATA, TEST_INPUT_NIR_MASK), -1)
    # Test with debug = "print"
    # Test with debug = "plot"
    # Test with debug = None
    device, white_balanced = pcv.white_balance(0, img, debug=None, roi=(5, 5, 80, 80))
    imgavg = np.average(img)
    balancedavg = np.average(white_balanced)
    assert balancedavg != imgavg


def test_plantcv_background_subtraction():
    # List to hold result of all tests.
    truths = []
    fg_img = cv2.imread(os.path.join(TEST_DATA, TEST_FOREGROUND))
    bg_img = cv2.imread(os.path.join(TEST_DATA, TEST_BACKGROUND))
    # Testing if background subtraction is actually still working.
    # This should return an array whose sum is greater than one
    device, fgmask = pcv.background_subtraction(background_image=bg_img, foreground_image=fg_img, device=0, debug=None)
    truths.append(np.sum(fgmask) > 0)
    # The same foreground subtracted from itself should be 0
    device, fgmask = pcv.background_subtraction(background_image=fg_img, foreground_image=fg_img, device=0, debug=None)
    truths.append(np.sum(fgmask) == 0)
    # The same background subtracted from itself should be 0
    device, fgmask = pcv.background_subtraction(background_image=bg_img, foreground_image=bg_img, device=0, debug=None)
    truths.append(np.sum(fgmask) == 0)
    # All of these should be true for the function to pass testing.
    assert (all(truths))
