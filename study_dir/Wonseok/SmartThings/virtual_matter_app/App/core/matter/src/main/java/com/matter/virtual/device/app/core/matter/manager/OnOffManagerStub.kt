package com.matter.virtual.device.app.core.matter.manager

import com.matter.virtual.device.app.DeviceApp
import com.matter.virtual.device.app.OnOffManager
import com.matter.virtual.device.app.core.common.MatterConstants
import javax.inject.Inject
import javax.inject.Singleton
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import timber.log.Timber

@Singleton
class OnOffManagerStub @Inject constructor(private val deviceApp: DeviceApp) : OnOffManager {

  private val _onOff = MutableStateFlow(false)
  val onOff: StateFlow<Boolean>
    get() = _onOff

  fun setOnOff(value: Boolean) {
    Timber.d("value:$value")
    _onOff.value = value
    deviceApp.setOnOff(MatterConstants.DEFAULT_ENDPOINT, value)
  }

  override fun initAttributeValue(endpoint: Int) {
    Timber.d("endpoint:$endpoint")
    deviceApp.setOnOff(endpoint, onOff.value)
  }

  override fun handleOnOffChanged(value: Boolean) {
    Timber.d("value:$value")
    _onOff.value = value
  }
}
