"""Helper functions for config tests."""


import copy
import time

from pytest import symbols

from . import utils


MAX_WAIT_DEPLOY = 10


def verify_config_produces_managed_svc(
        orchestration, bigip, param="", input_val=""):
    """Verify managed north-south service will deploy with given input."""
    config = _get_managed_northsouth_service_config(param, input_val)
    svc = utils.create_managed_northsouth_service(
        orchestration, config=config, wait_for_deploy=True
    )
    try:
        # - verify service is deployed
        assert svc.instances.count() > 0
        # - verify bigip objects created for managed service
        utils.wait_for_bigip_controller()
        backend_objs_exp = utils.get_backend_objects_exp(svc)
        assert utils.get_backend_objects(bigip) == backend_objs_exp
    except:
        raise
    finally:
        svc.delete()


def verify_config_produces_unmanaged_svc(
        orchestration, bigip, param="", input_val=""):
    """Verify managed north-south service will not deploy with given input."""
    config = _get_managed_northsouth_service_config(param, input_val)
    svc = utils.create_managed_northsouth_service(
        orchestration, config=config, wait_for_deploy=True
    )
    try:
        # - verify service is deployed
        assert svc.instances.count() > 0
        # - verify no bigip objects created for unmanaged service
        utils.wait_for_bigip_controller()
        assert utils.get_backend_objects(bigip) == {}
    except:
        raise
    finally:
        svc.delete()


def _get_managed_northsouth_service_config(param, input_val):
    config = copy.deepcopy(utils.DEFAULT_SVC_CONFIG)
    if symbols.orchestration == "marathon":
        if param == "partition":
            config['F5_PARTITION'] = input_val
        elif param == "bind_addr":
            config['F5_0_BIND_ADDR'] = input_val
        elif param == "port":
            config['F5_0_PORT'] = input_val
        elif param == "mode":
            config['F5_0_MODE'] = input_val
        elif param == "lb_algorithm":
            config['F5_0_BALANCE'] = input_val
    if symbols.orchestration == "k8s":
        frontend = config['data']['data']['virtualServer']['frontend']
        if param == "partition":
            frontend['partition'] = input_val
        elif param == "bind_addr":
            frontend['virtualAddress']['bindAddr'] = input_val
        elif param == "port":
            frontend['virtualAddress']['port'] = input_val
        elif param == "mode":
            frontend['mode'] = input_val
        elif param == "lb_algorithm":
            frontend['balance'] = input_val
    return config


def verify_bigip_controller_will_deploy(
        orchestration, param="", input_val=""):
    """Verify bigip-controller will deploy with given input."""
    config = _get_bigip_controller_config(param, input_val)
    controller = utils.create_bigip_controller(
        orchestration, config=config, wait_for_deploy=False
    )
    time.sleep(MAX_WAIT_DEPLOY)
    try:
        assert controller.instances.count() == 1
    except:
        raise
    finally:
        if symbols.orchestration == "k8s":
            orchestration.namespace = "kube-system"
        controller.delete()


def verify_bigip_controller_wont_deploy(
        orchestration, param="", input_val=""):
    """Verify bigip-controller will not deploy with given input."""
    config = _get_bigip_controller_config(param, input_val)
    controller = utils.create_bigip_controller(
        orchestration, config=config, wait_for_deploy=False
    )
    time.sleep(MAX_WAIT_DEPLOY)
    try:
        assert controller.instances.count() == 0
    except:
        raise
    finally:
        if symbols.orchestration == "k8s":
            orchestration.namespace = "kube-system"
        controller.delete()


def _get_bigip_controller_config(param, input_val):
    config = copy.deepcopy(utils.DEFAULT_F5MLB_CONFIG)
    if symbols.orchestration == "marathon":
        pass
    if symbols.orchestration == "k8s":
        pass
    return config