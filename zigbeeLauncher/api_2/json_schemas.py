config_schema = {
                "type": "object",
                "properties": {
                  "config": {
                    "type": "object",
                    "properties": {
                      "endpoints": {
                        "type": "array",
                        "items": {
                          "type": "object",
                          "properties": {
                            "client_clusters": {
                              "type": "array",
                              "items": {
                                "type": "object",
                                "properties": {
                                  "attributes": {
                                    "type": "array",
                                    "items": {
                                      "type": "object",
                                      "properties": {
                                        "default": {
                                          "oneOf": [
                                            {
                                              "type": "string"
                                            },
                                            {
                                              "type": "integer"
                                            }
                                          ]
                                        },
                                        "id": {
                                          "type": "integer"
                                        },
                                        "length": {
                                          "type": "integer"
                                        },
                                        "manufacturer": {
                                          "type": "boolean"
                                        },
                                        "manufacturer_code": {
                                          "type": "integer"
                                        },
                                        "name": {
                                          "type": "string"
                                        },
                                        "type": {
                                          "type": "string"
                                        },
                                        "writable": {
                                          "type": "boolean"
                                        }
                                      },
                                      "required": [
                                        "default",
                                        "id",
                                        "manufacturer",
                                        "name",
                                        "type",
                                        "writable"
                                      ],
                                      "x-apifox-orders": [
                                        "default",
                                        "id",
                                        "length",
                                        "manufacturer",
                                        "manufacturer_code",
                                        "name",
                                        "type",
                                        "writable"
                                      ],
                                      "x-apifox-ignore-properties": []
                                    }
                                  },
                                  "commands": {
                                    "type": "object",
                                    "properties": {
                                      "S->C": {
                                        "type": "array",
                                        "items": {
                                          "type": "object",
                                          "properties": {
                                            "description": {
                                              "type": "string"
                                            },
                                            "id": {
                                              "type": "integer"
                                            },
                                            "manufacturer": {
                                              "type": "boolean"
                                            },
                                            "manufacturer_code": {
                                              "type": "integer"
                                            }
                                          },
                                          "required": [
                                            "description",
                                            "id",
                                            "manufacturer"
                                          ],
                                          "x-apifox-orders": [
                                            "description",
                                            "id",
                                            "manufacturer",
                                            "manufacturer_code"
                                          ],
                                          "x-apifox-ignore-properties": []
                                        }
                                      },
                                      "C->S": {
                                        "type": "array",
                                        "items": {
                                          "type": "object",
                                          "properties": {
                                            "description": {
                                              "type": "string"
                                            },
                                            "id": {
                                              "type": "integer"
                                            },
                                            "manufacturer": {
                                              "type": "boolean"
                                            },
                                            "manufacturer_code": {
                                              "type": "integer"
                                            }
                                          },
                                          "required": [
                                            "description",
                                            "id",
                                            "manufacturer"
                                          ],
                                          "x-apifox-orders": [
                                            "description",
                                            "id",
                                            "manufacturer",
                                            "manufacturer_code"
                                          ],
                                          "x-apifox-ignore-properties": []
                                        }
                                      }
                                    },
                                    "required": [
                                      "S->C",
                                      "C->S"
                                    ],
                                    "x-apifox-orders": [
                                      "S->C",
                                      "C->S"
                                    ],
                                    "x-apifox-ignore-properties": []
                                  },
                                  "id": {
                                    "type": "integer"
                                  },
                                  "manufacturer": {
                                    "type": "boolean"
                                  },
                                  "manufacturer_code": {
                                    "type": "integer"
                                  },
                                  "name": {
                                    "type": "string"
                                  }
                                },
                                "required": [
                                  "attributes",
                                  "commands",
                                  "id",
                                  "manufacturer",
                                  "name"
                                ],
                                "x-apifox-orders": [
                                  "attributes",
                                  "commands",
                                  "id",
                                  "manufacturer",
                                  "manufacturer_code",
                                  "name"
                                ],
                                "x-apifox-ignore-properties": []
                              }
                            },
                            "device_id": {
                              "type": "integer"
                            },
                            "device_version": {
                              "type": "integer"
                            },
                            "id": {
                              "type": "integer"
                            },
                            "profile_id": {
                              "type": "integer"
                            },
                            "server_clusters": {
                              "type": "array",
                              "items": {
                                "type": "object",
                                "properties": {
                                  "attributes": {
                                    "type": "array",
                                    "items": {
                                      "type": "object",
                                      "properties": {
                                        "default": {
                                          "oneOf": [
                                            {
                                              "type": "string"
                                            },
                                            {
                                              "type": "integer"
                                            }
                                          ]
                                        },
                                        "id": {
                                          "type": "integer"
                                        },
                                        "length": {
                                          "type": "integer"
                                        },
                                        "manufacturer": {
                                          "type": "boolean"
                                        },
                                        "manufacturer_code": {
                                          "type": "integer"
                                        },
                                        "name": {
                                          "type": "string"
                                        },
                                        "type": {
                                          "type": "string"
                                        },
                                        "writable": {
                                          "type": "boolean"
                                        }
                                      },
                                      "required": [
                                        "default",
                                        "id",
                                        "manufacturer",
                                        "name",
                                        "type",
                                        "writable"
                                      ],
                                      "x-apifox-orders": [
                                        "default",
                                        "id",
                                        "length",
                                        "manufacturer",
                                        "manufacturer_code",
                                        "name",
                                        "type",
                                        "writable"
                                      ],
                                      "x-apifox-ignore-properties": []
                                    }
                                  },
                                  "commands": {
                                    "type": "object",
                                    "properties": {
                                      "S->C": {
                                        "type": "array",
                                        "items": {
                                          "type": "object",
                                          "properties": {
                                            "description": {
                                              "type": "string"
                                            },
                                            "id": {
                                              "type": "integer"
                                            },
                                            "manufacturer": {
                                              "type": "boolean"
                                            },
                                            "manufacturer_code": {
                                              "type": "integer"
                                            }
                                          },
                                          "required": [
                                            "description",
                                            "id",
                                            "manufacturer"
                                          ],
                                          "x-apifox-orders": [
                                            "description",
                                            "id",
                                            "manufacturer",
                                            "manufacturer_code"
                                          ],
                                          "x-apifox-ignore-properties": []
                                        }
                                      },
                                      "C->S": {
                                        "type": "array",
                                        "items": {
                                          "type": "object",
                                          "properties": {
                                            "description": {
                                              "type": "string"
                                            },
                                            "id": {
                                              "type": "integer"
                                            },
                                            "manufacturer": {
                                              "type": "boolean"
                                            },
                                            "manufacturer_code": {
                                              "type": "integer"
                                            }
                                          },
                                          "required": [
                                            "description",
                                            "id",
                                            "manufacturer"
                                          ],
                                          "x-apifox-orders": [
                                            "description",
                                            "id",
                                            "manufacturer",
                                            "manufacturer_code"
                                          ],
                                          "x-apifox-ignore-properties": []
                                        }
                                      }
                                    },
                                    "required": [
                                      "S->C",
                                      "C->S"
                                    ],
                                    "x-apifox-orders": [
                                      "S->C",
                                      "C->S"
                                    ],
                                    "x-apifox-ignore-properties": []
                                  },
                                  "id": {
                                    "type": "integer"
                                  },
                                  "manufacturer": {
                                    "type": "boolean"
                                  },
                                  "manufacturer_code": {
                                    "type": "integer"
                                  },
                                  "name": {
                                    "type": "string"
                                  }
                                },
                                "required": [
                                  "attributes",
                                  "commands",
                                  "id",
                                  "manufacturer",
                                  "name"
                                ],
                                "x-apifox-orders": [
                                  "attributes",
                                  "commands",
                                  "id",
                                  "manufacturer",
                                  "manufacturer_code",
                                  "name"
                                ],
                                "x-apifox-ignore-properties": []
                              }
                            }
                          },
                          "x-apifox-orders": [
                            "client_clusters",
                            "device_id",
                            "device_version",
                            "id",
                            "profile_id",
                            "server_clusters"
                          ],
                          "x-apifox-ignore-properties": []
                        }
                      },
                      "node": {
                        "type": "object",
                        "properties": {
                          "device_type": {
                            "type": "string"
                          },
                          "manufacturer_code": {
                            "type": "integer"
                          },
                          "radio_power": {
                            "type": "integer"
                          }
                        },
                        "required": [
                          "device_type",
                          "manufacturer_code",
                          "radio_power"
                        ],
                        "x-apifox-orders": [
                          "device_type",
                          "manufacturer_code",
                          "radio_power"
                        ],
                        "x-apifox-ignore-properties": []
                      }
                    },
                    "required": [
                      "endpoints",
                      "node"
                    ],
                    "x-apifox-orders": [
                      "endpoints",
                      "node"
                    ],
                    "x-apifox-ignore-properties": []
                  }
                },
                "required": [
                  "config"
                ],
                "x-apifox-orders": [
                  "config"
                ],
                "x-apifox-ignore-properties": []
              }
