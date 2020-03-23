import pathlib

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
                   alpha=.18, rad_fact=1.2, ret_changed=False,
                   ret_reused=False, count=None, max_count=None):
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
        created/updated (True) or whether only previously created ROI
        data was used (False).
    ret_reused: bool
        Return integer indicating how many previous fits
        were reused.
    count, max_count: multiprocessing.Value
        Can be used to monitor the progress of the algorithm.
        Initially, the value of `max_count.value` is incremented
        by the total number of steps. At each step, the value
        of `count.value` is incremented.
    """
    dir_out = pathlib.Path(dir_out).resolve()

    h5out = dir_out / FILE_SPHERE_DATA.format(method, model)
    statout = dir_out / FILE_SPHERE_STAT.format(method, model)

    with qpimage.QPSeries(h5file=h5roi, h5mode="r") as qps:
        dataid, roiparid, roiexclid = qps.identifier.split(":")
        cfgid = util.hash_object([r0,
                                  method,
                                  model,
                                  edgekw,
                                  imagekw if method == "image" else None,
                                  alpha,
                                  rad_fact])
    # Previous reference dataset may contain valuable fitting results
    h5ref = None
    changed = True
    reused = 0
    if util.is_series_file(h5out):
        with qpimage.QPSeries(h5file=h5out, h5mode="r") as qps_ref:
            refids = qps_ref.identifier.split(":")
            refids.pop(2)  # remove roiexclid from identifier
        if [dataid, roiparid, cfgid] == refids:
            # reuse (rename to temporary file)
            h5ref = h5out.with_suffix(".ref.h5")
            h5out.rename(h5ref)
            changed = False

    ids_ref = []
    if h5ref is not None:
        with qpimage.QPSeries(h5file=h5ref, h5mode="r") as qps_ref:
            ids_ref = [qpi["identifier"] for qpi in qps_ref]

    # initialize output file with identifier
    identifier = ":".join([dataid, roiparid, roiexclid, cfgid])
    with qpimage.QPSeries(h5file=h5out, h5mode="w",
                          identifier=identifier) as qps_out:
        pass

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

        if max_count is not None:
            with max_count.get_lock():
                max_count.value += len(qps_in)

        for qpi in qps_in:
            simident = "{}:{}".format(qpi["identifier"], model)
            if simident in ids_ref:
                with qpimage.QPSeries(h5file=h5ref, h5mode="r") as qps_ref:
                    qpi_sim = qps_ref[simident].copy()
                n = qpi_sim["sim index"]
                r = qpi_sim["sim radius"]
                c = qpi_sim["sim center"]
                ids_ref.remove(simident)
                reused += 1
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
                except qpsphere.models.excpt.UnsupportedModelParametersError:
                    print("Skipping object {} ".format(qpi["identifier"])
                          + "because unsupported model parameters were "
                          + "encountered.")
                    continue
                except BaseException as exc:
                    # Be more verbose
                    exc.args = ("ROI {}: ".format(qpi["identifier"])
                                + exc.args[0],)
                    raise
                else:
                    changed = True
            # write simulation results
            with qpimage.QPSeries(h5file=h5out, h5mode="a") as qps_out:
                qps_out.add_qpimage(qpi=qpi_sim, identifier=simident)
            # finally, update text file
            if "time" in qpi:
                qptime = qpi["time"]
            else:
                qptime = np.nan
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
            if count is not None:
                with count.get_lock():
                    count.value += 1

    if ids_ref:
        # leftovers
        changed = True
    # cleanup
    if h5ref is not None:
        h5ref.unlink()

    ret = [h5out]
    if ret_changed:
        ret.append(changed)
    if ret_reused:
        ret.append(reused)

    if len(ret) == 1:
        ret = ret[0]
    return ret


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
