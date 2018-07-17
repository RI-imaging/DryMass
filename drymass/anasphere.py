import pathlib
import warnings

import numpy as np
import qpimage
import qpsphere

from . import util

#: Output sphere analysis qpimage.QPSeries data
FILE_SPHERE_DATA = "sphere_{}_{}_data.h5"
#: Output sphere analysis statistics
FILE_SPHERE_STAT = "sphere_{}_{}_statistics.txt"


class EdgeDetectionFailedWarning(UserWarning):
    pass


def analyze_sphere(h5roi, dir_out, r0=10e-6, method="edge",
                   model="projection", edgekw={}, imagekw={},
                   alpha=.18, rad_fact=1.2, ret_changed=False):
    """Perform sphere analysis

    Parameters
    ----------
    h5series: str
        Path of qpimage.QPSeries hdf5 file
    dir_out: str
        Path to output directory
    r0: float
        Initial radius
    method: str
        Either "edge" or "image"; see :ref:`config_sphere` for
        more information.
    model: str
        Propagation model to use; see :ref:`config_sphere` for
        more information.
    edgekw: dict
        Keyword arguments to :func:`qpsphere.edgefit.contour_canny`
    imagekw: dict
        Keyword arguments to :func:`qpsphere.imagefit.alg.match_phase`
    alpha: float
        Refraction increment [mL/g]
    rad_fact: float
        Radial inclusion factor for dry mass computation
    ret_changed: bool
        Return boolean indicating whether the sphere data on disk was
        created/updated (True) or whether previously created ROI
        data was used (False).
    """
    dir_out = pathlib.Path(dir_out).resolve()

    h5out = dir_out / FILE_SPHERE_DATA.format(method, model)
    statout = dir_out / FILE_SPHERE_STAT.format(method, model)

    with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qps:
        cfgid = util.hash_object([qps,
                                  r0,
                                  method,
                                  model,
                                  edgekw,
                                  imagekw if method == "image" else None,
                                  alpha,
                                  rad_fact])

    create = mode_for_sphere_analysis(h5in=h5roi, h5out=h5out, cfgid=cfgid)

    # initialize file
    initmode = "w" if create else "r"
    with qpimage.QPSeries(h5file=h5out, h5mode=initmode) as qps_out:
        # get all simulation identifiers from previous analysis
        ids_out = [qpi["identifier"] for qpi in qps_out]

    with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qps_in, \
            statout.open(mode="w") as fd:

        header = ["identifier",
                  "index",
                  "radius_um",
                  "rel_dry_mass_pg",
                  "abs_dry_mass_pg",
                  "time",
                  "medium",
                  ]
        fd.write("#" + "\t".join(header) + "\r\n")

        for qpi in qps_in:
            simident = "{}:{}:sim:{}".format(qpi["identifier"], cfgid, model)
            if simident in ids_out:
                # read simulation results
                with qpimage.QPSeries(h5file=h5out, h5mode="r") as qps_out:
                    n = qps_out[simident]["sim index"]
                    r = qps_out[simident]["sim radius"]
                    c = qps_out[simident]["sim center"]
            else:
                try:
                    # fit sphere model
                    n, r, c, qpi_sim = qpsphere.analyze(qpi,
                                                        r0=r0,
                                                        method=method,
                                                        model=model,
                                                        edgekw=edgekw,
                                                        imagekw=imagekw,
                                                        ret_center=True,
                                                        ret_qpi=True)
                except qpsphere.edgefit.RadiusExceedsImageSizeError:
                    # Edge detection cannot proceed because the presumed
                    # object radius exceeds the image size. This might be
                    # the result of a "size variation" set too large.
                    msg = "Edge detection failed for ROI " \
                          + "{}! Try ".format(qpi["identifier"]) \
                          + "reducing the value of [roi]: 'size variation'."
                    warnings.warn(msg, EdgeDetectionFailedWarning)
                    # use dummy data
                    n = np.nan
                    r = np.nan
                    c = (np.nan, np.nan)
                    qpi_sim = qpsphere.simulate(radius=0,
                                                sphere_index=1,
                                                grid_size=qpi.shape)
                # write simulation results
                with qpimage.QPSeries(h5file=h5out, h5mode="a") as qps_out:
                    qps_out.add_qpimage(qpi=qpi_sim, identifier=simident)
            # finally, update text file
            if "time" in qpi:
                qptime = qpi["time"]
            else:
                qptime = 0
            data = {
                "identifier": qpi["identifier"],
                "index": n,
                "radius_um": r * 1e6,
                "abs_dry_mass_pg": absolute_dry_mass_sphere(
                    qpi=qpi,
                    radius=r,
                    center=c,
                    alpha=alpha,
                    rad_fact=rad_fact
                ) * 1e12,
                "rel_dry_mass_pg": relative_dry_mass(
                    qpi=qpi,
                    radius=r,
                    center=c,
                    alpha=alpha,
                    rad_fact=rad_fact
                ) * 1e12,
                "time": qptime,
                "medium": qpi["medium index"]
            }
            fd.write("\t".join([str(data[k]) for k in header]) + "\r\n")
            fd.flush()

    if ret_changed:
        return h5out, create
    else:
        return h5out


def absolute_dry_mass_sphere(qpi, radius, center, alpha=.18, rad_fact=1.2):
    """Compute absolute dry mass of a spherical phase object

    The absolute dry mass is computed with

    .. code::

        m_abs = m_rel + m_sup
        m_rel = lambda / (2*PI*alpha) * phi_tot * deltaA
        m_sup = 4*PI / (3*alpha) * radius^3 (n_med - n_PBS)

    with the vacuum wavelength ``lambda``, the total phase
    retardation in the area of interest ``phi_tot``, the pixel
    area ``deltaA``, the refractive index of the medium `n_med`
    (stored in ``qpi.meta``), and the refractive index of phosphate
    buffered saline (PBS) ``n_PBS=1.335``.

    This is the *absolute* dry mass, because it takes into account
    the offset caused by the suppressed density in the phase data.

    Parameters
    ----------
    qpi: qpimage.QPImage
        QPI data
    center: tuble (x,y)
        Center of the sphere [px]
    radius: float
        Radius of the sphere [m]
    wavelength: float
        The wavelength of the light [m]
    alpha: float
        Refraction increment [mL/g]
    rad_fact: float
        Inclusion factor that scales `radius` to increase
        the area used for phase summation; if the backgound
        phase exhibits a noise phase signal, positive and
        negative contributions cancel out and `rad_fact`
        does not have an effect above a certain critical value.

    Returns
    -------
    dry_mass: float
        The absolute dry mass of the sphere [g]
    """
    dm_rel = relative_dry_mass(qpi=qpi,
                               radius=radius,
                               center=center,
                               alpha=alpha,
                               rad_fact=rad_fact)
    medium_index = qpi["medium index"]
    dm_sup = 4 / 3 * np.pi / (alpha * 1e-6) * \
        radius**3 * (medium_index - 1.335)
    return dm_rel + dm_sup


def relative_dry_mass(qpi, radius, center, alpha=.18, rad_fact=1.2):
    """Compute relative dry mass of a circular area in QPI

    The dry mass is computed with

    m_rel = lambda / (2*PI*alpha) * phi_tot * deltaA

    with the vacuum wavelength `lambda`, the total phase
    retardation in the area of interest `phi_tot`, and the pixel
    area `deltaA`.

    This is the *relative* dry mass, because it is computed relative
    to the surrounding medium (phi_tot) and not relative to water.

    Parameters
    ----------
    qpi: qpimage.QPImage
        QPI data
    center: tuble (x,y)
        Center of the area of interest [px]
    radius: float
        Radius of the area of interest [m]
    wavelength: float
        The wavelength of the light [m]
    alpha: float
        Refraction increment [mL/g]
    rad_fact: float
        Inclusion factor that scales `radius` to increase
        the area used for phase summation; if the backgound
        phase exhibits a noise phase signal, positive and
        negative contributions cancel out and `rad_fact`
        does not have an effect above a certain critical value.

    Returns
    -------
    dry_mass: float
        The relative dry mass of the object [g]
    """
    image = qpi.pha
    rincl = radius / qpi["pixel size"] * rad_fact
    wavelength = qpi["wavelength"]
    sx, sy = qpi.shape
    x = np.arange(sx).reshape(-1, 1)
    y = np.arange(sy).reshape(1, -1)
    discsq = ((x - center[0])**2 + (y - center[1])**2)
    area = discsq < rincl**2
    phi_tot = np.sum(image[area])
    # compute dry mass
    pxarea = qpi["pixel size"]**2
    # convert alpha mL/g to m³/g
    fact = 1e-6
    # [kg]
    dm = wavelength / (2 * np.pi * alpha * fact) * phi_tot * pxarea
    return dm


def mode_for_sphere_analysis(h5in, h5out, cfgid):
    """Determine the mode for the QPSeries file for subsequent analysis

    Sometimes an analysis is interrupted and the output files are
    still intact. This method determines whether it is possible to
    continue the analysis where left off or not.

    Parameters
    ----------
    h5in: pathlib.Path
        The input QPSeries file
    h5out: pathlib.Path
        The output QPSeries file
    cfgid: str
        The configuration hash of the sphere analysis which is
        part of the output QPSeries analysis

    Returns
    -------
    create: bool
        Whether the output QPSeries file is ok. This is dependent
        on the following scenarios:

        - True: There is no output QPSeries file, it is corrupt,
              or at least one of the qpimage identifiers is not present
              in the input QPSeries.
        - False: Some of the input QPSeries identifiers are
              present in the output QPSeries.
    """
    with qpimage.QPSeries(h5file=h5in, h5mode="r") as qps_in:
        # read all identifiers
        idsin = [qpi["identifier"] for qpi in qps_in]

    try:
        with qpimage.QPSeries(h5file=h5out, h5mode="r") as qps_out:
            # read all identifiers
            idsout = [qpi["identifier"] for qpi in qps_out]
    except (IOError, OSError):
        # corrupt file
        idsout = []

    valid = []  # matching identifiers
    bad = []  # those exist in h5out but not in h5in

    for oid in idsout:
        iid, iicfg = oid.rsplit(":", 3)[:2]
        if iid in idsin and iicfg == cfgid:
            valid.append(iid)
        else:
            bad.append(iid)

    return bad or not valid
